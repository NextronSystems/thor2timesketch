# **THOR APT SCANNER** to Timesketch
This log conversion utility makes it easy to import [THOR](https://www.nextron-systems.com/thor/) logs into [Timesketch](https://timesketch.org/). Combining **THOR** findings on a shared timeline it enables cybersecurity analysts to enhance detection and analysis of malicious activity.

---
## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
   - [Prerequisites](#prerequisites)
   - [Installation Steps](#steps)
3. [Usage](#usage)
   - [Command-Line Arguments](#command-line-arguments)
   - [Examples](#examples)
4. [Configuration for Timesketch Ingestion](#configuration-for-timesketch-ingestion)
5. [Filter Configuration](#filter-configuration)
   - Standard THOR logs (JSON v1 / v2)
   - Audit-trail logs
6. [Input and Output Files](#input-and-output-files)
   - Input Files
   - Output File
7. [Ingesting into Timesketch](#ingesting-into-timesketch)
   - Manual Upload `jsonl`
   - Automatic Ingestion (`-s, --sketch`)
8. [Technical Details](#technical-details)
     - THOR JSON v1/v2
     - Audit-trail Logs
9. [Troubleshooting](#troubleshooting)
   - Issues and solutions
10. [Contributing](#contributing)
    - How to contribute
11. [License](./LICENSE)
12. [Support](#support)

---
## Overview


[![thor2ts](https://img.shields.io/badge/dynamic/json?label=thor2ts&query=%24.info.version&url=https://test.pypi.org/pypi/thor2timesketch/json)](https://test.pypi.org/project/thor2timesketch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)


**thor2ts** is a lightweight CLI utility that converts THOR security scanner logs into Timesketch-compatible JSONL format by:

* Extracting relevant fields from **THOR** logs

* Generating entries with the required Timesketch fields: message, datetime, and timestamp_desc

* Handling **THOR** events with multiple timestamps by creating separate entries for each timestamp

---
## Installation
### Prerequisites
Make sure you have the following installed on your system:
- [Git](https://git-scm.com/downloads)
- [Python 3.9](https://www.python.org/downloads/) or higher
- [Python venv package](https://docs.python.org/3/tutorial/venv.html)
 *(e.g., on Ubuntu/Debian: `sudo apt install python3-venv`)*
- [THOR JSON logs](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#json-output-json) Note: Scan with [--utc](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#utc) parameter to ensure timestamps are in UTC format.

### Steps
1. Create a virtual environment:

   * Linux / macOS (bash / zsh)
    ```bash
    python3 -m venv thor2ts-venv
    ```
   * Windows (cmd / powershell)
    ```cmd
    py -3 -m venv thor2ts-venv
    ```
2. Activate the virtual environment `thor2ts-venv`:

   * Linux / macOS (bash / zsh)
    ```bash
    source thor2ts-venv/bin/activate
    ```
   * Windows (cmd / powershell)
    ```cmd
    thor2ts-venv\Scripts\activate
    ```
3. Install thor2timesketch package:
    ```bash
    pip install thor2timesketch
    ```

4. Future Use

    To use `thor2ts` in the new terminal, activate the virtual environment, (see `step 2 - Activate the virtual environment` above).

---
## Usage
Once the virtual environment is active, you can run the tool from the command line:

```bash
thor2ts [input_file] [arguments]
```
### Command-Line Arguments

| Argument                         | Description                                                                                                             |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `<input-file>`                   | Path to the **THOR** JSON log file. **Required**.                                                                       |
| `-o, --output-file <JSONL_FILE>` | Save the converted **THOR** logs to the specified JSONL output file. **Optional**.                                      |
| `-s, --sketch <ID\|NAME>`        | Ingest directly into the specified Timesketch sketch (by ID or name). Auto-creates the sketch if missing. **Optional**. |
| `-b, --buffer-size <N>`          | Set the Timesketch importer buffer size (batch size) for ingestion. **Optional**.                                       |
| `-F, --filter <YAML_FILE>`       | Specify a YAML filter to select which **THOR** events are ingested. **Optional**.                                       |
| `--generate-filter`              | Generate `thor_filter.yaml` by extracting filters from **THOR** v1/v2 logs or using a default template. **Optional**.   |
| `-v, --verbose`                  | Enable verbose debugging output. **Optional**.                                                                          |
| `--version`                      | Display the current `thor2ts` version. **Optional**.                                                                    |

### Examples
| Scenario                           | Command                                                            |
|------------------------------------|--------------------------------------------------------------------|
| Convert to JSONL Output File       | `thor2ts thor_scan.json -o mapped_events.jsonl`                    |
| Convert & Ingest to Sketch         | `thor2ts thor_scan.json -s "THOR APT SCANNER"`                     |
| Set Custom Buffer Size             | `thor2ts thor_scan.json -s "THOR APT SCANNER" -b 100000`           |
| Convert, Filter & Ingest to Sketch | `thor2ts thor_scan.json -F thor_filter.yaml -s "THOR APT SCANNER"` |
| Extract Filter Template (file)     | `thor2ts input_v1.json --generate-filter`                          |
| Generate Default Filter Template   | `thor2ts --generate-filter`                                        |
| Enable Debug Mode                  | `thor2ts thor_scan.json -s "THOR APT SCANNER" --verbose`           |

---
## Configuration for Timesketch Ingestion

When you ingest for the first time (`-s, --sketch`), you will be prompted to enter your Timesketch connection settings:

1. **host_uri**
   URL of your Timesketch server (e.g. `https://timesketch.example.com`)

2. **auth_mode**
   Authentication mode:
   - `userpass` (username/password)
   - `oauth` (OAuth2)

3. **username**
   Timesketch USERNAME

4. **password**
   Timesketch password (**Note:** It will be tokenized and stored securely)

This creates two configuration files in the user's home directory $HOME/:

| File                   | Purpose                                             |
|------------------------|-----------------------------------------------------|
| `~/.timesketch.token`  | Encrypted authentication tokens                     |
| `~/.timesketchrc`      | Connection settings (host, auth mode, credentials)  |

### `~/.timesketchrc`
```ini
[timesketch]
host_uri = https://timesketch.example.com
username = USERNAME
verify = True
client_id = 
client_secret = 
auth_mode = userpass
cred_key = <generated_key>
```
For more detailed information about the Timesketch API client configuration and usage, please check out the [Timesketch API client documentation](https://timesketch.org/developers/api-client/).

___
## Filter Configuration

Thor2timesketch supports two filter scopes. The usage of filters is optional and sane defaults are used (that can be explicitly written to a config using the `--generate-filter` flag):

### 1. [Standard THOR logs (JSON v1 / v2)](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#json-output-json)

- **filters.levels**
  A list of THOR log `level` values to include (e.g., `Alert`, `Warning`).

- **filters.modules**
  - `include`: THOR log `module` names to include
  - `exclude`: THOR log `module` names to exclude

### 2. [Audit-trail logs](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#output-format)

- **filters.audit**
  - `info` — ingest all audit information entries
  - `findings` — ingest audit findings entries (then apply `filters.levels` + `filters.modules`)

### Example `thor_filter.yaml`

```yaml
filters:
  levels:
    - Alert
    - Warning
  modules:
    include:
      - Antivirus
      - Firewall
    exclude:
      - Debug
  audit:
    - info
    - findings
```

---
## Input and Output Files

Logs generated by [THOR APT SCANNER v10.7](https://www.nextron-systems.com/thor/).
### Input Files

- [**THOR JSON v1.0.0**](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#json-output-json) (generated by THOR 10.7 and earlier by default with `--jsonfile`)
- [**THOR JSON v2.0.0**](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#json-output-json) (can be generated by THOR 10.7 on request `--jsonv2`)
- [**Audit-trail** logs](https://thor-manual.nextron-systems.com/en/latest/usage/output-options.html#output-format) (very verbose log; new in v10.7; generate with `--audit-trail`)

### Output File

- **Timesketch-formatted JSONL**
  - If the target filename does not end with `.jsonl`, the extension will be automatically changed to `.jsonl`.
  - If the file already exists, new events are **appended** rather than overwritten.
### Warning
> Timesketch accepts only **JSON** files with a `.jsonl` extension. [Timesketch documentation](https://timesketch.org/guides/user/import-from-json-csv/)

---
## Ingesting into Timesketch
### 1. Manual Upload `jsonl`
- **Timesketch Web UI**
- [**Timesketch command line client (CLI)**](https://timesketch.org/guides/user/cli-client/)
### 2. Automatic Ingestion (`-s, --sketch`)
Add `-s, --sketch <ID|NAME>` to your `thor2ts` command and it will:

1. **Create or find** the specified sketch
2. **Push** the mapped events directly
3. **Wait** up to 60 seconds for indexing to finish
   - If indexing completes in time, you can go to the sketch immediately
   - Otherwise, ingestion continues in the background
4. **Buffer size** is set to 50,000 events by default, but you can adjust it with `-b, --buffer-size <N>`.
___
## Technical Details
### Field Mapping Logic

When a THOR record contains multiple timestamp fields, each timestamp is extracted into its own Timesketch event.
>All events derived from the same THOR log share a common `event_group_id` (a UUID) so you can correlate primary and secondary events.

### 1. THOR JSON v1/v2

#### **THOR event**
  - `message` ← original `"message"` (e.g. `"Malicious user details found"`)
  - `datetime` ← `"time"` (e.g. `2025-05-07T11:45:01+00:00`)
  - `timestamp_desc` ← `THOR scan timestamp`
  - `event_group_id` ← UUID generated per THOR event
  - `tag` ← `["thor", <Level>]` (e.g. `["thor","Alert"]`)
  - `**fields` ← all other fields from THOR log

- **Secondary events** (for each timestamp in THOR event)
  - `message` ← original `"message"` (e.g. `"Malicious user details found"`)
  - `datetime` ← time (e.g. `"last_logon"`)
  - `timestamp_desc` ← `"<module> - <field>"` (e.g. `Users - last_logon`)
  - `event_group_id` ← same UUID as THOR event
  - `tag` ← `["ts_extra", <Level>]`

### 2. Audit-trail Logs

#### **Info entries**

For each timestamp in `info`:
- `message` ← `Name` (e.g. `"File"`)
- `datetime` ← timestamp value (e.g. `2025-05-07T11:45:01+00:00`)
- `timestamp_desc` ← timestamp key (e.g. `accessed`)
- `tag` ← `["audit_info"]`
- `event_group_id` ← UUID for this audit record
- **First event** includes all other info fields

#### **Findings entries**

For each finding under `findings`:
- `message` ← finding’s `Message` (e.g. `"Malware file found"`)
- `datetime` ← timestamp value
- `timestamp_desc` ← `"<Module> - <field>"` (e.g. `Filescan - created`)
- `tag` ← `["findings", <Level>]` (e.g. `["findings","Alert"]`)
- `event_group_id` ← UUID for this audit record
- **First event** includes all other finding fields
>NOTE: Use `event_group_id` to correlate first and secondary events from the same THOR log or audit-trail log.

## Troubleshooting
_**Issues recorded on 20.05.2025**_

### 1. Multiple data sources created
- **Symptom:** Every ~50 000 events shows up as a separate data source in the sketch.
- **Cause:** The importer’s default batch size is [50 000 events](https://github.com/google/timesketch/blob/master/importer_client/python/timesketch_import_client/importer.py) per upload.
- **Solution:**
  1. Use the `-b, --buffer-size` argument to increase the batch size.
     ```bash
     thor2ts input.json -s "THOR APT SCANNER" -b 100000
     ```
  2. Convert to JSONL:
     ```bash
     thor2ts input.json -o mapped_events.jsonl
     ```
     Ingest the JSONL file into Timesketch using the CLI importer:
     ```bash
     timesketch_importer --sketch_id <ID> --threshold_entry 100000 mapped_events.jsonl
     ```
     > Warning: Consider RAM size when increasing batch size.

### 2. Timesketch host becomes unresponsive while ingesting THOR logs
- **Symptom:** High memory/CPU use, shell freezes, or Timesketch web UI becomes unresponsive during ingestion.
- **Cause:** OpenSearch (Timesketch backend) [allocates ~50 % of RAM for its JVM heap](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/auto-tune.html?utm_source=chatgpt.com), on < 16 GB systems this leaves too little memory for the OS and the *N* event-buffer used by the importer.
- **Solution:**
  - Run on a host with ≥ 16 GB RAM (recommended) for the default 50_000 event buffer size. Timesketch explicitly states 8GB is a minimum and ["the more the better"](https://timesketch.org/guides/admin/install/#:~:text=,setup%20SSL%20for%20the%20webserver)
  - Import in smaller batches using the `-b, --buffer-size` argument.

### 3. JSON Line format required
- **Symptom:** JSON parse errors.
- **Cause:** Input is pretty-printed JSON or a JSON array, not newline-delimited.
- **Solution:**
  - Use the unmodified THOR JSON output format or dump the THOR logs into JSON Lines format.

### 4. Web UI upload errors
- **Symptom:** Web UI rejects large `JSONL entries` `“Unterminated string in JSON at position ...”`.
- **Cause:** Browser-based uploader [can’t handle very large files](https://github.com/google/timesketch/issues/3243) or large JSONL entries
- **Solution**:
  - Ingest directly using `thor2ts` with the `-s, --sketch` argument.
  - Import via [CLI importer](https://timesketch.org/guides/user/cli-client/) for already mapped THOR events from a `JSONL` file:
  ```bash
  timesketch_importer --sketch_id <ID> mapped_events.jsonl
  ```
---
## Contributing
Contributions to `thor2ts` are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with your improvements or bug fixes.

---
## Support
If you encounter any issues or have questions, please open an issue in the [GitHub repository](https://github.com/NextronSystems/thor-ts-mapper.git/issues).

---
