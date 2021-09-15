const BASE_URL = 'https://api.spoonacular.com'


// Confirmation to delete an account

function confirmDelete() {
    let form = document.querySelector('#deleteForm')
    let msg = confirm('Are you sure? All recipes and information will also be deleted.');

    if (msg == true) {
        form.action = '/users/delete';
        form.method = 'POST';
    } else {
        return;
    }
}

