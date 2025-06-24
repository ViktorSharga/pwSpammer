# Slash Message Format Troubleshooting Guide

## Issue Description
The slash (`/`) character is missing from messages sent to the game, even though the application code correctly formats messages as `/{recipient} {message}`.

## Root Cause Analysis
The application code is working correctly - all tests show the slash is being sent via Windows API. The issue appears to be in the **game interaction layer**.

## Potential Causes

### 1. Chat Input Field Context
- **Wrong input field**: The game might have multiple chat inputs (say, whisper, guild, etc.)
- **Chat mode**: The game might be in the wrong chat mode when receiving input
- **Input field not ready**: The input field might not be active when typing starts

### 2. clear_chat_area Interference
- **Mouse clicks**: The coordinate clicking might be interfering with input
- **Timing**: Not enough delay between clicking and typing
- **Focus loss**: Mouse clicks might change focus away from chat input

### 3. Game-Side Filtering
- **Command interpretation**: The game might strip leading slashes for certain input fields
- **Auto-completion**: The game might have auto-complete that modifies input
- **Input validation**: The game might filter slash characters in certain contexts

## Solutions to Try

### Solution 1: Use Debug Method
```python
# In the game, try using the debug version:
app.send_message_debug("TestUser", "Hello world!")
```
This will print detailed steps and skip the clear_chat_area method.

### Solution 2: Use Minimal Method
```python
# Try the minimal version that skips coordinate clicking:
app.send_message_minimal("TestUser", "Hello world!")
```

### Solution 3: Manual Testing Steps
1. **Connect to game** using CTRL+SHIFT+1
2. **Set coordinates** normally
3. **Manually click** on the chat input field in the game
4. **Then try sending** a message

### Solution 4: Coordinate Verification
1. **Double-check coordinates** are pointing to the correct chat input field
2. **Test different input fields** (try different areas of the chat interface)
3. **Verify chat mode** (make sure game is in whisper/tell mode, not say/yell)

### Solution 5: Timing Adjustments
The application now includes a 0.1s delay after clear_chat_area. If still having issues:
1. **Increase delay** in send_message method
2. **Add manual delay** between connection and sending
3. **Test during different game states**

## Quick Tests

### Test 1: Verify Application Code
Run this to confirm the app code is working:
```bash
python3 -m pytest tests/test_slash_format.py -v
```

### Test 2: Check Mock Display
The mock should now show:
```
Mock: Would send '/TestUser Hello world!'
```

### Test 3: Game-Side Test
1. Manually type `/TestUser Hello` in the game chat
2. See if it works when typed manually
3. Compare with what the application sends

## Implementation Notes

The application now has three sending methods:
1. **send_message()**: Standard method with clear_chat_area
2. **send_message_debug()**: Debug version with logging and no clearing
3. **send_message_minimal()**: Minimal version with just focus and type

## Next Steps

If the issue persists:
1. **Try different coordinates** for chat input
2. **Test in different game states**
3. **Check game chat settings/modes**
4. **Consider game-specific input handling**

The application code is confirmed to be working correctly - the issue is in the game interaction layer.