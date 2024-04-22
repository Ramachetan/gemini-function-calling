document.addEventListener('DOMContentLoaded', () => {
  const observer = new MutationObserver((mutations, obs) => {
    const toolbar = document.querySelector('.MuiToolbar-root .MuiStack-root.css-1ytqtrj');
    if (toolbar) {
      // Create a wrapper for the dropdown to include the icon
      const dropdownWrapper = document.createElement('div');
      dropdownWrapper.className = 'dropdown-wrapper';
      dropdownWrapper.style.cssText = 'position: relative; display: inline-block;';

      // Create a select element (dropdown)
      const dropdown = document.createElement('select');
      dropdown.className = 'MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textPrimary MuiButton-sizeMedium MuiButton-textSizeMedium MuiButton-disableElevation css-1vhtqje';
      dropdown.style.cssText = 'cursor: pointer; appearance: none; -webkit-appearance: none; -moz-appearance: none; background: transparent; border: none; color: white; padding-right: 30px;';

      // Create default option "Select an option"
      const defaultOption = document.createElement('option');
      defaultOption.textContent = 'Select an option';
      defaultOption.disabled = true;
      defaultOption.selected = true;
      dropdown.appendChild(defaultOption);

      const option1 = document.createElement('option');
      option1.textContent = 'Unstructured';
      option1.value = 'https://genai-multi-rag-ford-rrcr7xvxjq-uc.a.run.app/chat';
      dropdown.appendChild(option1);

      const option2 = document.createElement('option');
      option2.textContent = 'Structured';
      option2.value = 'https://text2sql-function-calling-rrcr7xvxjq-uc.a.run.app/';
      dropdown.appendChild(option2);

      const option3 = document.createElement('option');
      option3.textContent = 'External';
      option3.value = 'https://gemini-function-calling-rrcr7xvxjq-uc.a.run.app/';
      dropdown.appendChild(option3);

      // Add dropdown icon
      const icon = document.createElement('i');
      icon.className = 'dropdown-icon';
      icon.style.cssText = 'position: absolute; right: 10px; top: 50%; transform: translateY(-50%); pointer-events: none; color: #00aae7';
      icon.textContent = '▼'; // Simple downward arrow as icon

      // Listen to changes in the dropdown
      dropdown.addEventListener('change', () => {
        window.location.href = dropdown.value;
      });

      // Append dropdown and icon to the wrapper, then append to the toolbar
      dropdownWrapper.appendChild(dropdown);
      dropdownWrapper.appendChild(icon);
      toolbar.appendChild(dropdownWrapper);

      // Stop observing after appending the dropdown
      obs.disconnect();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
});
