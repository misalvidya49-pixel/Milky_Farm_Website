// ================= SEARCH FUNCTION =================

function searchProducts() {
    let searchInput = document.getElementById("searchInput").value.toLowerCase().trim();
    let products = document.querySelectorAll(".product-card");

    products.forEach(function(product) {
        let productName = product.querySelector("h3").innerText.toLowerCase();

        if (productName.includes(searchInput)) {
            product.style.display = "block";
        } else {
            product.style.display = "none";
        }
    });
}


// ================= ENTER KEY SEARCH =================

document.addEventListener("DOMContentLoaded", function() {

    let searchInput = document.getElementById("searchInput");

    if (searchInput) {
        searchInput.addEventListener("keyup", function(event) {
            if (event.key === "Enter") {
                searchProducts();
            }
        });
    }

});