# Release notes

## 0.1.1

- Gameplay HUD adjusts automatically to ultrawide aspect ratios.
- Keeps existing icon/text sizes and left/centre/right anchors.
- Checks current HUD ownership and viewport every 500 ms without recurring
  global-object enumeration.
- Compares native UObject addresses, avoiding false changes from fresh Lua wrappers.
- Removes experimental screenshot keybinds and all menu modifications.
- Removes successful-application logging and limits compatibility/error warnings.

The gameplay layout change has been visually confirmed in multiple missions.
Automated lifecycle behaviour has mock coverage; this final packaging/performance
revision still needs an in-game mission-transition smoke test. No frame-time
benchmark has been performed.
