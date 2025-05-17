/**
 * Component loader for Common Cartridge
 * Handles loading of HTML components and initializes page interactivity
 */

const ComponentLoader = {
  // Load all components and initialize page
  loadComponents: function() {
    // Load all components in parallel
    Promise.all([
      fetch('components/page-header.html').then(response => response.text()),
      fetch('components/footer-navigation.html').then(response => response.text()),
      fetch('components/right-drawer.html').then(response => response.text())
    ]).then(([headerHtml, footerHtml, tocDrawerHtml]) => {
      // Insert components
      document.getElementById('header-container').innerHTML = headerHtml;
      document.getElementById('footer-container').innerHTML = footerHtml;
      document.getElementById('toc-drawer-container').innerHTML = tocDrawerHtml;
      
      // Initialize navigation first to ensure metadata is available
      Navigation.initNavigation();
      
      // Set page title in the header - this is a backup in case Navigation didn't set it
      const pageTitleElement = document.getElementById('page-title');
      if (pageTitleElement && !pageTitleElement.textContent) {
        pageTitleElement.textContent = document.title;
      }
      
      // Set PDF download link
      const pdfLinkElement = document.getElementById('download-pdf');
      if (pdfLinkElement && !pdfLinkElement.getAttribute('href')) {
        pdfLinkElement.href = "original.pdf";
      }
      
      // Initialize event listeners for TOC drawer
      this.initializeTOCDrawerListeners();
    });
  },

  // Initialize event listeners for TOC drawer
  initializeTOCDrawerListeners: function() {
    const tocToggleButtons = document.querySelectorAll('.toc-toggle');
    tocToggleButtons.forEach(button => {
      button.addEventListener('click', this.toggleTOC);
    });
    
    const tocToggleFooter = document.getElementById('toc-toggle-footer');
    if (tocToggleFooter) {
      tocToggleFooter.addEventListener('click', this.toggleTOC);
    }
    
    const closeButton = document.getElementById('toc-close');
    if (closeButton) {
      closeButton.addEventListener('click', this.closeTOC);
    }
    
    const backdrop = document.getElementById('toc-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', this.closeTOC);
    }
  },

  // Function to toggle TOC drawer
  toggleTOC: function() {
    const tocDrawer = document.getElementById('toc-drawer');
    const tocPanel = document.getElementById('toc-panel');
    
    if (tocDrawer.classList.contains('hidden')) {
      // Show TOC
      tocDrawer.classList.remove('hidden');
      setTimeout(() => {
        tocPanel.classList.remove('translate-x-full');
      }, 10);
    } else {
      // Hide TOC
      tocPanel.classList.add('translate-x-full');
      setTimeout(() => {
        tocDrawer.classList.add('hidden');
      }, 500);
    }
  },

  // Function to close TOC drawer
  closeTOC: function() {
    const tocDrawer = document.getElementById('toc-drawer');
    const tocPanel = document.getElementById('toc-panel');
    
    tocPanel.classList.add('translate-x-full');
    setTimeout(() => {
      tocDrawer.classList.add('hidden');
    }, 500);
  }
};

// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  ComponentLoader.loadComponents();
});