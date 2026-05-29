// Calculator UI Logic
// This script implements a simple calculator without external libraries.
// It directly manipulates the DOM elements defined in index.html.

// Grab the display element.
const display = document.getElementById('display');

// Internal state variables.
let currentInput = '';
let previousValue = null; // stores a number or null
let operator = null; // '+', '-', '*', '/' or null

/**
 * Append a digit (or decimal point) to the current input.
 * Handles leading zeroes and prevents multiple decimal points.
 * @param {string} number - The character pressed (e.g., '0'‑'9' or '.')
 */
function appendNumber(number) {
    // Ignore invalid characters.
    if (!/^[0-9.]$/.test(number)) return;

    // Prevent multiple decimal points.
    if (number === '.') {
        if (currentInput.includes('.')) return;
        // If input is empty, start with '0'.
        if (currentInput === '') {
            currentInput = '0';
        }
    }

    // Prevent leading zeros like "00" (except when a decimal follows).
    if (currentInput === '0' && number !== '.' ) {
        // Replace the leading zero with the new digit.
        currentInput = number;
    } else {
        currentInput += number;
    }
    updateDisplay();
}

/**
 * Choose an arithmetic operation.
 * If there is no current input but a previous value exists, just change the operator.
 * Otherwise, store the current input as the previous value and clear the input.
 * @param {string} op - One of '+', '-', '*', '/'
 */
function chooseOperation(op) {
    if (!['+','-','*','/'].includes(op)) return;
    if (currentInput === '' && previousValue !== null) {
        // Only change operator.
        operator = op;
        updateDisplay();
        return;
    }
    // If there is an existing pending operation, compute it first.
    if (previousValue !== null && operator && currentInput !== '') {
        compute();
    }
    // Store the current input as previousValue.
    previousValue = parseFloat(currentInput);
    operator = op;
    currentInput = '';
    updateDisplay();
}

/**
 * Perform the calculation based on previousValue, currentInput and operator.
 * Handles division‑by‑zero and updates the state accordingly.
 */
function compute() {
    if (operator === null || previousValue === null) {
        // Nothing to compute.
        return;
    }
    const a = previousValue;
    const b = currentInput === '' ? 0 : parseFloat(currentInput);
    let result;
    switch (operator) {
        case '+':
            result = a + b; break;
        case '-':
            result = a - b; break;
        case '*':
            result = a * b; break;
        case '/':
            if (b === 0) {
                // Show error and reset.
                display.textContent = 'Error';
                // Reset after a short delay.
                setTimeout(() => {
                    clearAll();
                }, 1500);
                return;
            }
            result = a / b; break;
        default:
            return;
    }
    // Prepare for next input.
    currentInput = result.toString();
    previousValue = null;
    operator = null;
    updateDisplay();
}

/**
 * Refresh the calculator display.
 */
function updateDisplay() {
    if (currentInput !== '') {
        display.textContent = currentInput;
    } else if (previousValue !== null) {
        display.textContent = previousValue.toString();
    } else {
        display.textContent = '0';
    }
}

/**
 * Reset the calculator to its initial state.
 */
function clearAll() {
    currentInput = '';
    previousValue = null;
    operator = null;
    updateDisplay();
}

/**
 * Central click handler using event delegation.
 * Buttons must define `data-type` (number, operator, equals, clear)
 * and `data-value` (the actual character/value).
 * @param {Event} event
 */
function handleButtonClick(event) {
    const target = event.target;
    if (!target.dataset) return;
    const type = target.dataset.type;
    const value = target.dataset.value;
    if (!type) return;
    switch (type) {
        case 'number':
            appendNumber(value);
            break;
        case 'operator':
            chooseOperation(value);
            break;
        case 'equals':
            compute();
            break;
        case 'clear':
            clearAll();
            break;
        default:
            // Unknown type – ignore.
            break;
    }
}

// Attach the delegated listener once the DOM is ready.
function init() {
    const buttonsGrid = document.querySelector('.buttons-grid');
    if (buttonsGrid) {
        buttonsGrid.addEventListener('click', handleButtonClick);
    }
    // Optional: keyboard support could be added later.
    updateDisplay();
}

document.addEventListener('DOMContentLoaded', init);
