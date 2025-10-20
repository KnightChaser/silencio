# src/silencio/core/redact.py
from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI
from ..settings import get_openai_api_key, get_model_name

SYSTEM_PROMPT = """
You are a redaction engine for corporate security and confidentiality.

Return a DEDUPED list with fields: item, code, desc, aliases, notes.
- One row per unique item present in the input. If an item appears multiple times, list it ONCE.
- Use the most specific code: (1|2|3|4)(A–E|X)?(a–e|x)?  e.g., (1)(A)(c), (3)(B)(d), (2)(C).
- Keep item EXACTLY as it appears in the input (surface form). Add other seen surface forms to aliases.
- Be minimal and factual. Do not include anything not present in the input.
- Note that first, second, and third category number must be enclosed by small brackets respectively, like "(3)(A)(b)".
  (Not 3.A.b or [3][A][b], 3(A)(b), etc.)

Legend:
---

### (1) Personally Identifiable Information (PII)

**(1)(A) Contact identifiers**

* (1)(A)(a) Real names: real names of specific personnel.
* (1)(A)(b) Pseudonames: alternative names of a specific person, such as usernames of a website, nicknames, or other written names.
* (1)(A)(c) E-mail addresses: any e-mail addresses of a specific person.
* (1)(A)(d) Telephone numbers: any telephone numbers of a specific person.
* (1)(A)(e) Social Media Handlers (IDs): any social media account IDs (handles) that uniquely identify a specific person.
* (1)(A)(x) Other contact identifiers: other similar contact identifiers.

**(1)(B) Numeric identifiers**

* (1)(B)(a) Non-legal/private number identifiers: employee IDs, customer IDs, etc.
* (1)(B)(b) Legal number identifiers: passport numbers, national IDs, social security numbers, or any legally binding national identifiers.
* (1)(B)(c) Financial number identifiers: bank account numbers, credit card numbers, CVV numbers, and other finance-related identifiers.
* (1)(B)(x) Other numeric identifiers: uncategorized numeric identifiers.

**(1)(C) Location identifiers**

* (1)(C)(a) Written addresses: home, office, or postal addresses that can identify a specific location.
* (1)(C)(b) Geological data: coordinates or geological numeric data.
* (1)(C)(x) Other location identifiers: uncategorized location identifiers.

**(1)(D) Indirect PII (Quasi-identifiers)**

* (1)(D)(a) Employment context: job titles, project assignments, internal team data that could identify a person when combined.
* (1)(D)(b) Technical device identifiers: hardware serials, hostnames tied to individuals, browser fingerprints, MAC addresses, etc.
* (1)(D)(c) Behavioral data: writing styles, activity timestamps, login habits, command patterns, voiceprints, etc.
* (1)(D)(d) Metadata linkage: file ownerships, Git metadata, author tags, EXIF data, internal user IDs, etc.
* (1)(D)(x) Other indirect PII: uncategorized indirect identifiers.

---

### (2) Company and Partner Information

* (2)(A) Corporate identities: company/organization names, brands, logos, and identifiers not meant for disclosure.
* (2)(B) Affiliates and brands: subsidiaries, affiliated entities, and their identifiers not meant for disclosure.
* (2)(C) Internal project details: non-public project names, details, or identifiers.
* (2)(X) Other enterprise details: uncategorized company or partner information.

---

### (3) Technical Details

**(3)(A) Authentication and access credentials**

* (3)(A)(a) Service IDs and passwords: logins or credentials for systems and tools.
* (3)(A)(b) API keys: credentials for APIs or web services (e.g., AWS, Google Cloud).
* (3)(A)(c) Tokens: authentication or access tokens (e.g., OAuth, JWTs, session tokens).
* (3)(A)(d) Cryptographic authentication data: SSH keys, private/public key pairs, internal CA certs, etc.
* (3)(A)(x) Other credentials: other uncategorized credential materials.

**(3)(B) System and network configurations**

* (3)(B)(a) Network topologies and addressing: IP schemas, DNS zones, routing rules.
* (3)(B)(b) Access control and firewall rules: ACLs, SIEM/IDS rules, firewall configs.
* (3)(B)(c) Host and environment identifiers: hostnames, internal domains, cloud instance names.
* (3)(B)(d) Configuration files and manifests: YAMLs, JSONs, system configs, database configs, etc.
* (3)(B)(x) Other configurations: miscellaneous or unclassified system configurations.

**(3)(C) Source code, analytic logic, and exploit materials**

* (3)(C)(a) Signatures and detection rules: IOCs, YARA rules, regex detection logic.
* (3)(C)(b) Source code and snippets: program code, pseudocode, logic fragments.
* (3)(C)(c) Exploits and payloads: exploit PoCs, shellcode, malware binaries, network payloads.
* (3)(C)(d) Service or architecture diagrams: infrastructure or workflow diagrams.
* (3)(C)(e) Analytical or heuristic content: proprietary techniques or analysis logic.
* (3)(C)(x) Other business logics or methods: uncategorized analytical logic.

**(3)(D) Operational evidence and system trace**

* (3)(D)(a) Memory or crash dumps: RAM captures, core dumps, crash logs.
* (3)(D)(b) System or application logs: sensitive log output from internal systems.
* (3)(D)(c) Network captures: PCAPs, dumps, or extracted traffic.
* (3)(D)(d) Embedded identifiers and metadata: UUIDs, paths, device IDs, timestamps, metadata.
* (3)(D)(x) Other system traces: other forensic or runtime evidence.

**(3)(E) Visual and attached materials**

* (3)(E)(a) Screenshots and media: captures of tools, dashboards, or sensitive visuals.
* (3)(E)(b) Diagrams or charts: network or process diagrams containing sensitive info.
* (3)(E)(c) Tool interfaces: screenshots of proprietary tools or panels.
* (3)(E)(d) Files or file listings: directory listings or filenames that imply sensitive content.
* (3)(E)(e) Links (URLs): internal or shared-drive URLs or attachment paths.
* (3)(E)(x) Other attachments: other uncategorized sensitive materials.

---

### (4) Confidential and Legal Details

* (4)(A) Contracts and agreements: legal or business contracts and related data.
* (4)(B) Financial data: revenues, invoices, balances, or other financial information.
* (4)(C) Security: data requiring protection for private, national, or critical infrastructure security.
* (4)(D) Miscellaneous: privileged communications, investigations, or uncategorized confidential/legal data.
"""


class RedactionItem(BaseModel):
    item: str  # exact surface from found in the documentation
    code: str  # e.g., "(3)(A)(b)"
    desc: str  # short label, e.g., "API keys"
    aliases: List[str] = Field(default_factory=List)  # other surface forms seen
    notes: str = ""  # optional short reason


class RedactionInventory(BaseModel):
    items: List[RedactionItem]


def enumerate_confidential_items(document_text: str) -> RedactionInventory:
    """
    Ask the model to enumerate unique confidential items in 'document_text',
    and add return a strongly-typed RedactionInventory.
    """
    client = OpenAI(api_key=get_openai_api_key())
    model = get_model_name()

    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": document_text},
        ],
        text_format=RedactionInventory,
    )
    return response.output_parsed or RedactionInventory(items=[])
