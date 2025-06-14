// Tab functionality
function openTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show the selected tab content
    document.getElementById(tabId).classList.add('active');
    
    // Activate the clicked tab button
    event.currentTarget.classList.add('active');
}

// File input display
document.getElementById('csvFile').addEventListener('change', function(e) {
    const fileName = document.getElementById('fileName');
    if (this.files.length > 0) {
        fileName.textContent = `File dipilih: ${this.files[0].name}`;
    } else {
        fileName.textContent = '';
    }
});

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Load expenses from API
async function loadExpenses() {
    try {
        const response = await fetch('/api/expenses');
        const data = await response.json();
        
        if (data.status === 'success') {
            renderExpenses(data.data);
            updateMiniChart(data.data);
            updateBudgetProgress(data.data);
        }
    } catch (error) {
        console.error('Error loading expenses:', error);
    }
}

// Render expenses to table
function renderExpenses(expenses) {
    const tbody = document.getElementById('expenseTable');
    tbody.innerHTML = '';
    
    // Show last 10 expenses in reverse order (newest first)
    expenses.slice(-10).reverse().forEach((expense, index) => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${expense.nama}</td>
            <td>${expense.kategori}</td>
            <td>${formatCurrency(expense.jumlah)}</td>
            <td>${expense.tanggal}</td>
            <td>
                <button class="btn-delete" onclick="deleteExpense(${expenses.length - 1 - index})">
                    <i class="fas fa-trash"></i> Hapus
                </button>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Delete expense
async function deleteExpense(index) {
    if (confirm('Apakah Anda yakin ingin menghapus pengeluaran ini?')) {
        try {
            const response = await fetch(`/api/expenses/${index}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                loadExpenses(); // Refresh the list
            } else {
                alert('Gagal menghapus pengeluaran: ' + (result.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error deleting expense:', error);
            alert('Terjadi kesalahan saat menghapus pengeluaran');
        }
    }
}


// Update budget progress
function updateBudgetProgress(expenses) {
    const incomeInput = document.getElementById('income');
    if (!incomeInput || !incomeInput.value) return;
    
    const income = parseFloat(incomeInput.value);
    const totalExpenses = expenses.reduce((sum, exp) => sum + exp.jumlah, 0);
    const remaining = income - totalExpenses;
    const percentage = (totalExpenses / income) * 100;
    
    const progressFill = document.getElementById('budgetProgress');
    const budgetStatus = document.getElementById('budgetStatus');
    
    progressFill.style.width = `${Math.min(percentage, 100)}%`;
    budgetStatus.textContent = `Sisa Anggaran: ${formatCurrency(remaining)} | ${percentage.toFixed(1)}% digunakan`;
    
    // Change color based on percentage
    if (percentage > 80) {
        progressFill.style.backgroundColor = '#e74c3c'; // Red
    } else if (percentage > 50) {
        progressFill.style.backgroundColor = '#f39c12'; // Orange
    } else {
        progressFill.style.backgroundColor = '#2ecc71'; // Green
    }
}

// Update mini chart
function updateMiniChart(expenses) {
    const ctx = document.getElementById('miniChart').getContext('2d');
    
    // Group by category
    const categories = {};
    expenses.forEach(exp => {
        categories[exp.kategori] = (categories[exp.kategori] || 0) + exp.jumlah;
    });
    
    // Destroy previous chart if exists
    if (window.miniChartInstance) {
        window.miniChartInstance.destroy();
    }
    
    // Create new chart
    window.miniChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categories),
            datasets: [{
                data: Object.values(categories),
                backgroundColor: [
                    '#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6',
                    '#1abc9c', '#d35400', '#34495e', '#7f8c8d', '#27ae60'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: 'Distribusi Pengeluaran per Kategori',
                    font: {
                        size: 16
                    }
                }
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
}

// Upload CSV file
async function uploadCSV() {
    const fileInput = document.getElementById('csvFile');
    if (fileInput.files.length === 0) {
        alert('Pilih file CSV terlebih dahulu');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const result = await response.text();
            alert(result);
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Terjadi kesalahan saat mengupload file');
    }
}

// Form submission - Income
document.getElementById('incomeForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // In a real app, you might want to save this to localStorage or send to server
    updateBudgetProgress(await getExpenses());
});

// Form submission - Expense
document.getElementById('expenseForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        nama: document.getElementById('expenseName').value,
        jumlah: document.getElementById('amount').value,
        kategori: document.getElementById('category').value,
        tanggal: document.getElementById('date').value
    };
    
    try {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Clear form
            document.getElementById('expenseForm').reset();
            
            // Refresh data
            loadExpenses();
        } else {
            alert('Gagal menambahkan pengeluaran: ' + (result.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding expense:', error);
        alert('Terjadi kesalahan saat menambahkan pengeluaran');
    }
});

// Helper function to get expenses
async function getExpenses() {
    try {
        const response = await fetch('/api/expenses');
        const data = await response.json();
        return data.data || [];
    } catch (error) {
        console.error('Error fetching expenses:', error);
        return [];
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadExpenses();
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
}); 
