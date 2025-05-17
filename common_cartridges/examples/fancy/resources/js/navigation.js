/**
 * Common Cartridge Navigation and UI Functionality
 */
document.addEventListener('DOMContentLoaded', function() {
  // Load components
  loadComponent('header-container', 'components/page-header.html', function() {
    // Set the page title based on the document title
    document.getElementById('page-title').textContent = document.title;
    
    // Set PDF link
    const pdfLink = document.getElementById('download-pdf');
    if (pdfLink) pdfLink.href = 'original.pdf';
    
    // Add event listeners for TOC toggle buttons
    const tocToggleButtons = document.querySelectorAll('.toc-toggle');
    tocToggleButtons.forEach(button => {
      button.addEventListener('click', toggleTOC);
    });
  });

  loadComponent('footer-container', 'components/footer-navigation.html', function() {
    // Get the current page path
    const currentPath = window.location.pathname;
    const filename = currentPath.substring(currentPath.lastIndexOf('/') + 1);
    
    // Update navigation links based on page structure
    updateNavigationLinks(filename);
    
    // Add event listener for footer TOC toggle
    const tocToggleFooter = document.getElementById('toc-toggle-footer');
    if (tocToggleFooter) {
      tocToggleFooter.addEventListener('click', toggleTOC);
    }
  });

  loadComponent('toc-drawer-container', 'components/right-drawer.html', function() {
    // Add event listener for close button
    const closeButton = document.getElementById('toc-close');
    if (closeButton) {
      closeButton.addEventListener('click', closeTOC);
    }
    
    // Add event listener for backdrop
    const backdrop = document.getElementById('toc-backdrop');
    if (backdrop) {
      backdrop.addEventListener('click', closeTOC);
    }
    
    // Highlight current page in TOC
    highlightCurrentPageInTOC();
  });
});

/**
 * Load component HTML into a container
 */
function loadComponent(containerId, componentPath, callback) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  fetch(componentPath)
    .then(response => response.text())
    .then(html => {
      container.innerHTML = html;
      if (typeof callback === 'function') {
        callback();
      }
    })
    .catch(error => {
      console.error(`Error loading component ${componentPath}:`, error);
    });
}

/**
 * Toggle TOC drawer visibility
 */
function toggleTOC() {
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
}

/**
 * Close TOC drawer
 */
function closeTOC() {
  const tocDrawer = document.getElementById('toc-drawer');
  const tocPanel = document.getElementById('toc-panel');
  
  tocPanel.classList.add('translate-x-full');
  setTimeout(() => {
    tocDrawer.classList.add('hidden');
  }, 500);
}

/**
 * Highlight current page in TOC
 */
function highlightCurrentPageInTOC() {
  const currentPath = window.location.pathname;
  const filename = currentPath.substring(currentPath.lastIndexOf('/') + 1);
  
  const tocLinks = document.querySelectorAll('.toc-content a');
  tocLinks.forEach(link => {
    if (link.getAttribute('href') === filename) {
      link.classList.add('bg-primary-50', 'text-primary-600', 'current-page');
    } else {
      link.classList.remove('bg-primary-50', 'text-primary-600', 'current-page');
    }
  });
}

/**
 * Update navigation links based on page structure
 */
function updateNavigationLinks(currentPage) {
  // Page structure mapping
  const pageStructure = {
    'page1.html': { 
      prev: null, 
      next: { url: 'page2.html', title: 'Section 1.1: Getting Started' }
    },
    'page2.html': { 
      prev: { url: 'page1.html', title: 'Chapter 1: Introduction' }, 
      next: { url: 'page3.html', title: 'Section 1.2: Key Concepts' }
    },
    'page3.html': { 
      prev: { url: 'page2.html', title: 'Section 1.1: Getting Started' }, 
      next: { url: 'page4.html', title: 'Section 1.3: Summary' }
    },
    'page4.html': { 
      prev: { url: 'page3.html', title: 'Section 1.2: Key Concepts' }, 
      next: null
    }
  };
  
  // Get page data
  const pageData = pageStructure[currentPage];
  if (!pageData) return;
  
  const prevPageLink = document.getElementById('prev-page-link');
  const prevPageTitle = document.getElementById('prev-page-title');
  const nextPageLink = document.getElementById('next-page-link');
  const nextPageTitle = document.getElementById('next-page-title');
  
  // Update prev link
  if (pageData.prev) {
    prevPageLink.href = pageData.prev.url;
    prevPageTitle.textContent = pageData.prev.title;
    prevPageLink.classList.remove('invisible');
  } else {
    prevPageLink.classList.add('invisible');
  }
  
  // Update next link
  if (pageData.next) {
    nextPageLink.href = pageData.next.url;
    nextPageTitle.textContent = pageData.next.title;
    nextPageLink.classList.remove('invisible');
  } else {
    nextPageLink.classList.add('invisible');
  }
}