// Signing in
const RegisterButton = document.getElementById("RegisterButton");

let NameCreds;
let Email;
let Password;
let ConfirmPassword;
let RegisterAsOption;

if(RegisterButton){
    RegisterButton.onclick = function(event){

        event.preventDefault();

        NameCreds = document.getElementById("NameCredentails").value;
        Email = document.getElementById("EmailCredentials").value;
        Password = document.getElementById("PasswordCredentials").value;
        ConfirmPassword = document.getElementById("ConfirmPasswordCredentials").value;
        RegisterAsOption = document.getElementById("RegisterAsOptions").value;

        let FieldData = [NameCreds, Email, Password, ConfirmPassword, RegisterAsOption];

        let IfallFilled = FieldData.every(field => field.trim() !== "");

        if(!IfallFilled) {
            return window.alert(`All the fields have not been filled. Please fill all the fields!`);
        }

        if(Password !== ConfirmPassword) {
            return window.alert(`All fields entered, but passwords do not match.`);
        }

        if(Password.length < 8){
            return window.alert(`Enter a password with 8 or more characters!`)
        }

        fetch("/api/register", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            NAME: NameCreds,
            EMAIL: Email,
            PASS: Password,
            ROLE: RegisterAsOption
        })
    })

    .then(result => result.json())

    .then(data => {
        if (data.success) {
            window.alert(data.message);
            window.location.href = '/Login'
        }

        else {
            window.alert(data.message);
        }

    })

    .catch(error => {
        console.error(error);
        window.alert(`Server Error`);
    })
};
}

// For logging in
const LoginButton = document.getElementById("LoginButton")

if(LoginButton){
    LoginButton.onclick = function(event){
    event.preventDefault();

    const LoginPassword = document.getElementById("LoginPassword").value;
    const EmailPassword = document.getElementById("EmailPassword").value;

    if(!EmailPassword || !LoginPassword) {
        return window.alert("Please fill in all the fields!");
    }

    fetch("/api/Login", {

        method: "POST",
        
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            EMAILPASS: EmailPassword,
            LOGINPASS: LoginPassword
        })
    })

    .then(response => response.json())

    .then(data =>{

        if (data.success){
            window.alert(data.message);
            
            if(data.role.toLowerCase() === "donor") {
                window.alert(`Taking you to: ${data.role} Dashboard`)
                window.location.href = "/DonorDashboard"
            }
            else if(data.role.toLowerCase() === "receiver") {
                window.alert(`Taking you to: ${data.role} Dashboard`)
                window.location.href = "/ReceiverDashboard"
            }
            else {
                window.location.href = "/"
            }
        }

        else {
            window.alert(data.message);
        }
    })

    .catch(error => {
        console.error(error);
        window.alert("Server Error");
    });
};
}

// For logging out
function logout(){

    fetch("/api/Logout", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        }

    })

    .then(response => response.json())

    .then(data => {

        if(data.success) {
            window.location.href = "/Login";
        }
    })

    .catch(error => {
        console.error(`Logout error`, error);

        window.location.href = "/Login";
    });

}

function SubmitProduct() {
    window.location.href = "/AddProducts"
}

const AddNewProduct = document.getElementById("AddProductButton")

if(AddNewProduct) {
    AddNewProduct.onclick = function(event) {
        event.preventDefault();
        
        const formData = new FormData();

        const ProductImage = document.getElementById("productImage").files[0];
        const ExpiryHours = document.getElementById("productExpiry").value;

        formData.append("productName", document.getElementById("productName").value);
        formData.append("description", document.getElementById("productDesc").value);
        formData.append("price", document.getElementById("productPrice").value);
        formData.append("stock", document.getElementById("productStock").value);
        formData.append("phonenumber", document.getElementById("productPhoneNumber").value);
        formData.append("productImage", ProductImage);
        formData.append('expiryHours', ExpiryHours)

        fetch("/api/AddProducts", {

            method: "POST",

            body: formData
        })

        .then(response => response.json())

        .then(data => {
            if(data.success) {
                window.alert(`Product Added!`);
                window.location.href = '/DonorProducts';
            }
        })

        .catch(error => {
            console.error(`Server Error`, error);
        })
    }
}

function DeletProducteButton(productName) {
    if(!confirm(`Are you sure you want to delete ${productName}?`)) return;

    fetch('/api/DeleteProduct', {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({name: productName})
    })

    .then(response => response.json())

    .then(data => {
        window.alert(data.message);

        if(data.success) {
            location.reload();
        }
    })

    .catch(error => {
        console.error("Error", error);
    })
}

async function crearOrderButton(Pname, Pprice, DEmail) {
    const confirmation = confirm(`Place order for ${Pname}?`);
    if(!confirmation) return;

    try {
        const response = await fetch('/api/CreateOrder', {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                productName: Pname,
                productPrice: Pprice,
                donorEmail: DEmail
            })
        });

        const result = await response.json();

        if(result.success) {
            window.alert(result.message);
            window.location.href = '/ReceiverOrders';
        }
        else {
            window.alert(`Order Failed: ` + result.message)
        }
    }

    catch(error) {
        console.error(`Network Error`, error);
        window.alert(`Could not connect to the server.`)
    }
}

async function UpdateOrderStatus(ID, NewStatus) {
    if(!confirm(`Mark Order #${ID} as ${NewStatus}?`)) return;

    const response = await fetch('/api/UpdateOrderStatus', {

        method: "POST",
        
        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            orderID: ID,
            status: NewStatus
        })
    });

    const result = await response.json();

    if(result.success) {
        window.alert(result.message);
        window.location.href = '/DonorOrders'
    }
}