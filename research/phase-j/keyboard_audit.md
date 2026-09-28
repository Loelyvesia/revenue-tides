# Keyboard audit

**Result: PASS.**

- First Tab reaches the skip link; its 3 px focus outline is visible. Enter activates `#main-content`.
- Prism series select is followed by the focusable Quarter Prism region, then Previous/Next and native quarter controls in logical order.
- Left/Right Arrow changes the selected quarter while the Prism region has focus; boundary buttons disable normally.
- Space opens source disclosure; Finding evidence, Observatory rows, method/source disclosure, and normal source links are native keyboard controls.
- Focus remains on the initiating control after a quarter change. No automatic focus transfer or trap occurs.
- Direct quarter buttons expose `aria-current`; all nine Observatory rows are keyboard reachable.
- Hash navigation, Back, and Forward passed: F1 → F2 → Back to F1 → Forward to F2.

The browser smoke recorded more than 20 visible keyboard-reachable controls in the full workflow and no unreachable critical information.
