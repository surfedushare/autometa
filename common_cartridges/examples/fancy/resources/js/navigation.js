/**
 * Navigation utilities for Common Cartridge
 * Uses the global MANIFEST object defined in each HTML page
 */

// Helper functions for navigation based on MANIFEST
const Navigation = {
  // Get current page resource from URL
  getCurrentResource: function() {
    const currentPath = window.location.pathname;
    const filename = currentPath.substring(currentPath.lastIndexOf('/') + 1);
    
    // Find the resource by its href
    for (const resourceId in MANIFEST.resources) {
      const resource = MANIFEST.resources[resourceId];
      const resourceFilename = resource.href.substring(resource.href.lastIndexOf('/') + 1);
      if (resourceFilename === filename) {
        return resource;
      }
    }
    return null;
  },

  // Find an item based on its associated resource identifier
  findItemByResourceRef: function(resourceRef, items = null) {
    // Start from root items if not specified
    if (!items) {
      items = MANIFEST.organizations[0].items;
    }
    
    // Check current level
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.resourceRef === resourceRef) {
        return item;
      }
      
      // Check children recursively
      if (item.children && item.children.length > 0) {
        const found = this.findItemByResourceRef(resourceRef, item.children);
        if (found) {
          return found;
        }
      }
    }
    
    return null;
  },

  // Get next page (if exists)
  getNextPage: function(currentResourceId) {
    // Build flat navigation order
    const navOrder = this.buildFlatNavigation();
    
    // Find current position
    for (let i = 0; i < navOrder.length; i++) {
      if (navOrder[i].resourceRef === currentResourceId) {
        // Return next page if exists
        if (i < navOrder.length - 1) {
          return navOrder[i + 1];
        }
      }
    }
    
    return null;
  },

  // Get previous page (if exists)
  getPreviousPage: function(currentResourceId) {
    // Build flat navigation order
    const navOrder = this.buildFlatNavigation();
    
    // Find current position
    for (let i = 0; i < navOrder.length; i++) {
      if (navOrder[i].resourceRef === currentResourceId) {
        // Return previous page if exists
        if (i > 0) {
          return navOrder[i - 1];
        }
      }
    }
    
    return null;
  },

  // Build a flat navigation order array from the hierarchical structure
  buildFlatNavigation: function() {
    const navOrder = [];
    
    const traverseItems = (items) => {
      for (const item of items) {
        navOrder.push(item);
        if (item.children && item.children.length > 0) {
          traverseItems(item.children);
        }
      }
    };
    
    traverseItems(MANIFEST.organizations[0].items);
    return navOrder;
  },

  // Build table of contents HTML for the drawer
  buildTableOfContents: function() {
    let html = '<ul class="space-y-1">';
    
    const buildItemHtml = (items, level = 0) => {
      let itemsHtml = '';
      const padding = level * 0.5;
      
      for (const item of items) {
        const resource = MANIFEST.resources[item.resourceRef];
        if (!resource) continue;
        
        itemsHtml += `<li>
          <a href="${resource.href.split('/').pop()}" 
             class="block rounded-md px-3 py-2 text-sm font-medium ${level > 0 ? `pl-${3 + padding}` : ''} 
             text-gray-700 hover:bg-gray-50 hover:text-gray-900">
            ${item.title}
          </a>
        </li>`;
        
        if (item.children && item.children.length > 0) {
          itemsHtml += buildItemHtml(item.children, level + 1);
        }
      }
      
      return itemsHtml;
    };
    
    html += buildItemHtml(MANIFEST.organizations[0].items);
    html += '</ul>';
    
    return html;
  },

  // Initialize navigation based on the current page and MANIFEST
  initNavigation: function() {
    // Get current resource
    const currentResource = this.getCurrentResource();
    if (!currentResource) return;
    
    // Get associated item
    const currentItem = this.findItemByResourceRef(currentResource.identifier);
    if (!currentItem) return;

    // Set PDF link if available
    const pdfResource = MANIFEST.resources.RESOURCE_PDF;
    if (pdfResource) {
      const pdfLink = document.getElementById('download-pdf');
      if (pdfLink && !pdfLink.getAttribute('href')) {
        pdfLink.href = pdfResource.href.split('/').pop();
      }
    }
    
    // Setup navigation links
    const prevPageLink = document.getElementById('prev-page-link');
    const nextPageLink = document.getElementById('next-page-link');
    
    if (prevPageLink) {
      const prevPage = this.getPreviousPage(currentResource.identifier);
      if (prevPage) {
        prevPageLink.href = MANIFEST.resources[prevPage.resourceRef].href.split('/').pop();
        const prevPageTitle = document.getElementById('prev-page-title');
        if (prevPageTitle) prevPageTitle.textContent = prevPage.title;
        prevPageLink.classList.remove('invisible');
      } else {
        prevPageLink.classList.add('invisible');
      }
    }
    
    if (nextPageLink) {
      const nextPage = this.getNextPage(currentResource.identifier);
      if (nextPage) {
        nextPageLink.href = MANIFEST.resources[nextPage.resourceRef].href.split('/').pop();
        const nextPageTitle = document.getElementById('next-page-title');
        if (nextPageTitle) nextPageTitle.textContent = nextPage.title;
        nextPageLink.classList.remove('invisible');
      } else {
        nextPageLink.classList.add('invisible');
      }
    }
    
    // Build table of contents
    const tocContent = document.querySelector('.toc-content');
    if (tocContent) {
      tocContent.innerHTML = this.buildTableOfContents();
      
      // Highlight current page
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
  }
};

// No timeouts - initialize navigation right after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Navigation will be called after components are loaded in the page's script
});
