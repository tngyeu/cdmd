# WordCraft document work

For creating or editing Word documents in this workspace, follow the user's WordCraft MCP workflow in WORDCRAFT_MCP.md.

- Prefer WordCraft Desktop MCP at 127.0.0.1:7981 and the configured server `wordcraft`.
- Use MCP new_document, open_document, type_text, select_text, execute, batch, inspect_document, get_text, render_page and save_document for document authoring and verification.
- Do not use mouse/keyboard simulation, screen coordinates, GUI automation, or MCP click/key tools to author documents. If MCP lacks a required function, report the limitation; do not switch to GUI.
- Inspect the current document before replacing it. Preserve unsaved user content. The user explicitly requests editing the named file in place: save changes to that same path, without creating additional deliverable versions or suffixes unless the user asks. Current main file: Ban_trinh_bay_bo_sung_Duy_Tan_29-10-2026_da_can_chinh.docx.
- Verify content, formatting and rendering after saving/reopening. Do not promise complete fidelity for untested complex documents.
- A missing tool in the current chat is different from a failed MCP server. The diagnostic stdio MCP client and logs are in tmp/wordcraft_mcp_setup_20261029. It calls real MCP tools, not GUI automation.
- Do not start drafting the official supplemental statement until the user requests it after setup.
