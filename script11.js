// ✅ Validate Admin Login
function validateLogin(event) {
    event.preventDefault();
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    if (email === "admin@example.com" && password === "admin123") {
        window.location.href = "dashboard.html";
    } else {
        document.getElementById("login-error").textContent = "Invalid credentials!";
    }
}

// ✅ Edit Order Status
function editStatus(element) {
    let statusOptions = ["Pending", "Shipped"];
    let dropdown = document.createElement("select");

    statusOptions.forEach(status => {
        let option = document.createElement("option");
        option.value = status;
        option.textContent = status;
        dropdown.appendChild(option);
    });

    dropdown.value = element.textContent;
    dropdown.onchange = function () {
        element.textContent = dropdown.value;
    };

    element.replaceWith(dropdown);
}

// ✅ Attach Event Listeners to Edit Icons
function attachEventListeners() {
    document.querySelectorAll(".edit-icon").forEach(icon => {
        icon.removeEventListener("click", enableEditing);
        icon.addEventListener("click", enableEditing);
    });
}

// ✅ Enable Editing for Product Fields
function enableEditing(event) {
    let parent = event.target.closest(".editable");
    let type = parent.dataset.type;
    
    if (type === "image") {
        editImage(parent);
    } else if (type === "text") {
        editText(parent);
    } else if (type === "category") {
        editCategory(parent);
    } else if (type === "price" || type === "quantity") {
        editNumber(parent, type);
    }
}

// ✅ Edit Product Image
function editImage(parentElement) {
    let imgElement = parentElement.querySelector("img");
    let url = prompt("Enter Image URL:", imgElement.src);
    if (url) {
        imgElement.src = url;
    }
}

// ✅ Edit Product Name
function editText(parentElement) {
    let textElement = parentElement.querySelector(".editable-text");
    let input = document.createElement("input");
    
    input.type = "text";
    input.value = textElement.textContent;
    input.classList.add("edit-input");

    input.addEventListener("blur", () => {
        textElement.textContent = input.value;
        parentElement.replaceChild(textElement, input);
    });

    input.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            textElement.textContent = input.value;
            parentElement.replaceChild(textElement, input);
        }
    });

    parentElement.replaceChild(input, textElement);
    input.focus();
}

// ✅ Edit Product Price or Quantity
function editNumber(parentElement, type) {
    let textElement = parentElement.querySelector(".editable-text");
    let input = document.createElement("input");
    
    input.type = "number";
    input.value = textElement.textContent.replace("$", "");
    input.classList.add("edit-input");

    input.addEventListener("blur", () => {
        textElement.textContent = type === "price" ? `$${input.value}` : input.value;
        parentElement.replaceChild(textElement, input);
    });

    input.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            textElement.textContent = type === "price" ? `$${input.value}` : input.value;
            parentElement.replaceChild(textElement, input);
        }
    });

    parentElement.replaceChild(input, textElement);
    input.focus();
}

// ✅ Edit Product Category with Dropdown
function editCategory(parentElement) {
    let textElement = parentElement.querySelector(".editable-text");
    let categories = ["Cake", "Cookies", "Bread"];
    let dropdown = document.createElement("select");

    categories.forEach(cat => {
        let option = document.createElement("option");
        option.value = cat;
        option.textContent = cat;
        dropdown.appendChild(option);
    });

    dropdown.value = textElement.textContent;

    dropdown.addEventListener("blur", () => {
        textElement.textContent = dropdown.value;
        parentElement.replaceChild(textElement, dropdown);
    });

    dropdown.addEventListener("change", () => {
        textElement.textContent = dropdown.value;
        parentElement.replaceChild(textElement, dropdown);
    });

    parentElement.replaceChild(dropdown, textElement);
    dropdown.focus();
}

// ✅ Add Product with Editable Fields
function addProduct() {
    let table = document.getElementById("productTable");
    let row = table.insertRow();

    row.innerHTML = `
        <td class="editable" data-type="image">
            <img src="https://via.placeholder.com/50" class="product-img">
            <span class="edit-icon">✏️</span>
        </td>
        <td class="editable" data-type="text">
            <span class="editable-text">New Product</span>
            <span class="edit-icon">✏️</span>
        </td>
        <td class="editable" data-type="category">
            <span class="editable-text">Cake</span>
            <span class="edit-icon">✏️</span>
        </td>
        <td class="editable" data-type="price">
            <span class="editable-text">$0</span>
            <span class="edit-icon">✏️</span>
        </td>
        <td class="editable" data-type="quantity">
            <span class="editable-text">1</span>
            <span class="edit-icon">✏️</span>
        </td>
    `;

    attachEventListeners(); // Ensure new elements get event listeners
}

// ✅ Run when DOM is Loaded
document.addEventListener("DOMContentLoaded", function () {
    attachEventListeners();
});
function toggleStatusDropdown(element) {
    let dropdown = element.nextElementSibling;
    dropdown.style.display = "inline-block"; // Show the dropdown
}

function updateStatus(dropdown) {
    let selectedValue = dropdown.value;
    let statusSpan = dropdown.previousElementSibling;

    // Update the status text
    statusSpan.textContent = selectedValue;

    // Change status color dynamically
    if (selectedValue === "Shipped") {
        statusSpan.style.background = "#99ff99";
    } else {
        statusSpan.style.background = "#ff9999";
    }

    dropdown.style.display = "none"; // Hide dropdown after selection
}
document.addEventListener("DOMContentLoaded", function () {
    attachEventListeners();
    document.getElementById("addProductBtn").addEventListener("click", addProduct);
});
// ✅ Run when DOM is Loaded
document.addEventListener("DOMContentLoaded", function () {
    loadProductsFromStorage();
    attachEventListeners();
    document.getElementById("addProductBtn").addEventListener("click", addProduct);
});

// ✅ Load Products from Local Storage
function loadProductsFromStorage() {
    let products = JSON.parse(localStorage.getItem("products")) || [];
    let table = document.getElementById("productTable").querySelector("tbody");
    table.innerHTML = ""; // Clear old rows

    products.forEach(product => {
        addProductToTable(product);
    });
}

// ✅ Save Products to Local Storage
function saveProductsToStorage() {
    let products = [];
    document.querySelectorAll("#productTable tbody tr").forEach(row => {
        let product = {
            image: row.cells[0].querySelector("img").src,
            name: row.cells[1].querySelector(".editable-text").textContent,
            category: row.cells[2].querySelector(".editable-text").textContent,
            price: row.cells[3].querySelector(".editable-text").textContent.replace("$", ""),
            quantity: row.cells[4].querySelector(".editable-text").textContent
        };
        products.push(product);
    });

    localStorage.setItem("products", JSON.stringify(products));
}
