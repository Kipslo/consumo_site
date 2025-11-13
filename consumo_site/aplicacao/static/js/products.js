
function getProducts(){
    let cookies = document.cookie.split("; ");
    for (let cookie of cookies){
        const [name, value] = cookie.split("=");
        if (name === "products"){
            let products = value.split("|");
            for (let i = 0; i < products.length - 1; i++){
                products[i] = products[i].split(",-");
                products[i][6] = products[i][6].split(".-");
            }
            products[products.length - 1] = products[products.length - 1].split(",-")
            console.log(products)
            //return [[nameProduct, categoryid, tipe, price, printer, quantity, [note1, note2, ...]], [...], [number1, number2, ...] ]
            return products
        }
    }
    return null


}
function saveProducts(products){
    console.log(products)
    //product format = [[nameProduct, categoryid, tipe, price, printer, quantity, [note1, note2, ...]], [...], [number1, number2, ...] ]
    for (let i = 0; i< products.length - 1; i++){
        products[i][6] = products[i][6].join(".-");
        products[i] = products[i].join(",-");
    }
    products[products.length - 1] = products[products.length - 1].join(",-");
    products = products.join("|");
    console.log(products)
    products = products + "; path=/commands";
    document.cookie = "products=" + products;
};
function insertProduct(name, category, tipe, price, printer, size, number){
    let products = getProducts();
    if (tipe === "SIZE"){
        name = name + "(" + size + ")";
    }
    if (products === null){
        products = [[name, category, tipe, price, printer, "1", ["", ]] , [number, ]];
    } else {
        if (!(products[products.length - 1][0] === number) || products[products.length - 1][0] === "null"){
            products = [[name, category, tipe, price, printer, "1", ["", ]] , [number, ]];
            console.log(products)
        } else {
            products.splice(products.length - 1, 0, [name, category, tipe, price, printer, "1", ["", ]]);
        }
    }
    console.log(products)
    saveProducts(products)
}
function deleteProduct(index){
    let products = getProducts();
    products.splice(index, 1);
    saveProducts(products);
    location.reload();
}
