function deleteUser(userid){
    fetch('/delete-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ userid: userid })
    }).then((_res) => {
        window.location.href = '/userlist';
    })
}


function addToCart(productId) {
    const quantity = document.getElementById('quantity-' + productId).value;
    console.log(quantity)
    fetch(`/add_to_cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Added to cart!");
            // Update cart UI or reload the page
        } else {
            alert("Failed to add to cart.");
        }
    });
}