// Main JavaScript file for PromptVault

// Wait for DOM to be loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize copy buttons
    if (typeof initCopyButtons === 'function') {
        initCopyButtons();
    }
    
    // Initialize search functionality
    if (typeof initSearch === 'function') {
        initSearch();
    }
});

/**
 * Show an alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const mainContainer = document.querySelector('main.container');
    if (mainContainer) {
        mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
    }
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

/**
 * Initialize copy buttons functionality
 */
function initCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const content = this.getAttribute('data-content');
            copyToClipboard(content, this);
        });
    });
}

/**
 * Copy text to clipboard and show feedback
 * @param {string} text - Text to copy
 * @param {HTMLElement} button - Button element for feedback
 */
function copyToClipboard(text, button) {
    // Modern clipboard API
    navigator.clipboard.writeText(text).then(() => {
        // Store original text
        const originalText = button.textContent;
        
        // Change button text to show success
        button.textContent = 'Copied!';
        button.classList.add('btn-success');
        button.classList.remove('btn-primary');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        
        // Show error feedback
        button.textContent = 'Failed to copy';
        button.classList.add('btn-danger');
        button.classList.remove('btn-primary');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            button.textContent = 'Copy';
            button.classList.remove('btn-danger');
            button.classList.add('btn-primary');
        }, 2000);
    });
}

/**
 * Initialize live search functionality with debounce
 */
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    
    if (searchInput) {
        // Debounce function to limit search requests
        const debounce = (fn, delay) => {
            let timeoutId;
            return function(...args) {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }
                timeoutId = setTimeout(() => {
                    fn.apply(this, args);
                }, delay);
            };
        };
        
        // Function to perform search
        const performSearch = debounce(function(e) {
            const query = e.target.value.trim();
            
            // Only search if query has at least 2 characters
            if (query.length >= 2) {
                fetchSearchResults(query);
            } else if (query.length === 0) {
                // If search is cleared, show all prompts
                fetchSearchResults('');
            }
        }, 300); // 300ms debounce
        
        // Add event listener to search input
        searchInput.addEventListener('input', performSearch);
    }
}

/**
 * Fetch search results via AJAX
 * @param {string} query - Search query
 */
function fetchSearchResults(query) {
    // Get search results container
    const resultsContainer = document.querySelector('.search-results');
    
    if (!resultsContainer) return;
    
    // Show loading indicator
    resultsContainer.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    
    // Fetch search results from API
    fetch(`/api/prompts/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            // Render search results
            renderSearchResults(data, resultsContainer);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            resultsContainer.innerHTML = '<div class="alert alert-danger">An error occurred while searching. Please try again.</div>';
        });
}

/**
 * Render search results in the container
 * @param {Object} data - Search results data
 * @param {HTMLElement} container - Container element
 */
function renderSearchResults(data, container) {
    // Clear container
    container.innerHTML = '';
    
    const prompts = data.prompts;
    
    if (prompts.length === 0) {
        // No results found
        container.innerHTML = '<div class="alert alert-info">No prompts found matching your search.</div>';
        return;
    }
    
    // Create results HTML
    const resultsHTML = prompts.map(prompt => {
        // Format categories and tags
        const categories = prompt.categories.map(cat => 
            `<span class="badge bg-primary">${cat.name}</span>`
        ).join(' ');
        
        const tags = prompt.tags.map(tag => 
            `<span class="badge bg-secondary">${tag.name}</span>`
        ).join(' ');
        
        // Create card for prompt
        return `
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="card-title mb-0">${prompt.title}</h5>
                    </div>
                    <div class="card-body">
                        <p class="card-text">${prompt.description ? truncateText(prompt.description, 150) : 'No description available'}</p>
                        ${categories ? `<div class="mb-2">${categories}</div>` : ''}
                        ${tags ? `<div>${tags}</div>` : ''}
                    </div>
                    <div class="card-footer">
                        <a href="/prompts/${prompt.id}" class="btn btn-sm btn-outline-primary">View Details</a>
                        <button class="btn btn-sm btn-outline-primary copy-btn" data-content="${prompt.content}">Copy</button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Add results to container
    container.innerHTML = `<div class="row">${resultsHTML}</div>`;
    
    // Add pagination if needed
    if (data.pagination.total_pages > 1) {
        addPagination(data.pagination, container);
    }
}

/**
 * Add pagination controls to search results
 * @param {Object} pagination - Pagination metadata
 * @param {HTMLElement} container - Container element
 */
function addPagination(pagination, container) {
    const { page, total_pages } = pagination;
    
    // Create pagination HTML
    let paginationHTML = `
        <nav aria-label="Search results pagination">
            <ul class="pagination justify-content-center">
                <li class="page-item ${page === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${page - 1}">Previous</a>
                </li>
    `;
    
    // Add page numbers
    for (let i = 1; i <= total_pages; i++) {
        paginationHTML += `
            <li class="page-item ${i === page ? 'active' : ''}">
                <a class="page-link" href="#" data-page="${i}">${i}</a>
            </li>
        `;
    }
    
    paginationHTML += `
                <li class="page-item ${page === total_pages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${page + 1}">Next</a>
                </li>
            </ul>
        </nav>
    `;
    
    // Add pagination to container
    container.insertAdjacentHTML('beforeend', paginationHTML);
    
    // Add event listeners to pagination links
    const paginationLinks = container.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const pageNum = parseInt(this.getAttribute('data-page'));
            if (!isNaN(pageNum) && pageNum > 0) {
                // Get current search query
                const query = document.querySelector('.search-input').value.trim();
                
                // Fetch search results for the selected page
                fetchSearchResults(query, pageNum);
            }
        });
    });
}

/**
 * Truncate text to specified length with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} - Truncated text
 */
function truncateText(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}
