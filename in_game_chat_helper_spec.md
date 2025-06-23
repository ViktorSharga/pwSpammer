# 🧩 In-Game Chat Helper – Functional Specification

## Overview
A lightweight, modern-looking Python desktop application for Windows, built to assist users with managing chat interactions in the online game **Asgard Perfect World**.

---

## 🔧 Tabs & Features

### 1. **MemberList Tab**

#### Features
- Scrollable single-column list of members.
- **Top Control Buttons**:
  - **Add from Clipboard**: Adds clipboard content (≤ 100 characters) to the list.
  - **Add**: Adds a new editable entry.
  - **Edit**: Enables editing of the selected entry (active only if selected).
  - **Remove**: Deletes selected entry (active only if selected).
  - **Delete All**: Clears the list with confirmation prompt.

- **Bottom Buttons**:
  - **SAVE**: Saves the list to a JSON file.
  - **LOAD**: Loads list from a JSON file.

---

### 2. **Templates Tab**

#### Features
- Display templates as tiles, each showing:
  - **Short Name**
  - **Message Content** (max 300 characters)

- **Control Buttons**:
  - **Add**: Opens dialog for short name + content.
  - **Edit**: Opens dialog to modify selected tile.
  - **Remove**: Deletes selected tile.

---

### 3. **Spammer Tab**

#### Layout
- **Recipient Area (Top)**:
  - Scrollable checkbox dropdown of members (from MemberList).
  - All selected by default.
  - Button: **Unselect All**
  - Display: `"X recipients selected"`

- **Message Area (Bottom)**:
  - Read-only field for message preview.
  - Dropdown to select template.
  - **Edit**: Opens manual editor to modify content.
  - **Send Next** (mock): Sends message to first selected recipient and unselects them.
  - **Send All** (mock): Sends message to all selected recipients with 500ms delay.

#### Send Logic
- `sendNext()`:
  - `ClearChatArea()`
  - `sendString("/<nickname> <message>")`
  - `sendEnter()`
  - Unselects recipient and updates count
  - Logs: `→ Sent <templateName> to <memberName>`

- `sendAll()`:
  - Same as `sendNext`, but in a loop with 500ms cooldown
  - Button changes to **Stop**
  - Can be interrupted

- **Lock Area (Bottom of App)**:
  - Displays real-time message logs
  - Active during sending

---

### 4. **Setup Tab**

#### Connection Management
- **Status**: CONNECTED or UNCONNECTED
- **Hotkey**: `CTRL+SHIFT+1`
  - When pressed:
    - Captures the focused window.
    - Validates it belongs to `elementclient.exe` with title `Asgard Perfect World`.
    - Registers window handle and PID.
    - Status updates to CONNECTED with PID shown.

- **Test Connection**:
  - Brings registered game window to focus.

#### Chat Calibration
- **Set Coordinate 1**:
  - Focuses game window, captures user click (Coord1)

- **Set Coordinate 2**:
  - Same as above (Coord2)

- **Display Saved Coordinates**:
  - Coord1, Coord2 shown in UI

- **Test**:
  - Calls `ClearChatArea()` for validation

#### Method: ClearChatArea()
- Brings game window into focus
- Clicks:
  1. `Coord2`
  2. Wait 100ms
  3. `Coord1`

Purpose: Ensure chat input is active and ready.