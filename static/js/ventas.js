console.log("VENTAS JS CARGADO");

document.addEventListener("DOMContentLoaded", () => {

    const hoy = new Date();

    const fechaLocal = hoy.getFullYear() + "-" +
        String(hoy.getMonth() + 1).padStart(2, "0") + "-" +
        String(hoy.getDate()).padStart(2, "0");

    document.getElementById("fechaVenta").value = fechaLocal;
});

function generarTabla(id, clase){

    let body = document.getElementById(id);

    for(let i=0;i<20;i++){

        let fila = "<tr>";

        for(let j=0;j<6;j++){

            fila += `
            <td>
            <input type="number"
            class="peso ${clase}"
            step="0.01">
            </td>
            `;
        }

        fila += "</tr>";

        body.innerHTML += fila;
    }
}

generarTabla("bodyComercial","comercial");
generarTabla("bodyJumbo","jumbo");
generarTabla("bodyPardo","pardo");

function calcular(){

    let totalComercial=0;
    let totalJumbo=0;
    let totalPardo=0;

    document.querySelectorAll(".comercial").forEach(x=>{
        totalComercial += Number(x.value)||0;
    });

    document.querySelectorAll(".jumbo").forEach(x=>{
        totalJumbo += Number(x.value)||0;
    });

    document.querySelectorAll(".pardo").forEach(x=>{
        totalPardo += Number(x.value)||0;
    });

    document.getElementById("pesoTotalComercial").value = totalComercial.toFixed(2);
    document.getElementById("pesoTotalJumbo").value = totalJumbo.toFixed(2);
    document.getElementById("pesoTotalPardo").value = totalPardo.toFixed(2);

    let precioComercial = Number(document.getElementById("precioComercial").value)||0;
    let precioJumbo = Number(document.getElementById("precioJumbo").value)||0;
    let precioPardo = Number(document.getElementById("precioPardo").value)||0;

    let importeComercial = totalComercial * precioComercial;
    let importeJumbo = totalJumbo * precioJumbo;
    let importePardo = totalPardo * precioPardo;

    document.getElementById("importeComercial").value = importeComercial.toFixed(2);
    document.getElementById("importeJumbo").value = importeJumbo.toFixed(2);
    document.getElementById("importePardo").value = importePardo.toFixed(2);

    document.getElementById("importeGeneral").value =
        (importeComercial + importeJumbo + importePardo).toFixed(2);
}

document.addEventListener("input", calcular);

function mostrarTablas(){

    document.getElementById("contenedorTablas").style.display = "flex";

    document.getElementById("seccionComercial").style.display =
        document.getElementById("chkComercial").checked ? "block" : "none";

    document.getElementById("seccionJumbo").style.display =
        document.getElementById("chkJumbo").checked ? "block" : "none";

    document.getElementById("seccionPardo").style.display =
        document.getElementById("chkPardo").checked ? "block" : "none";
}

function agregarPesoAutomatico(valor, tipo){

    let celdas = document.querySelectorAll("." + tipo);

    const filas = 20;
    const columnas = 6;

    for(let columna = 0; columna < columnas; columna++){

        for(let fila = 0; fila < filas; fila++){

            let indice = fila * columnas + columna;

            if(celdas[indice].value === ""){

                celdas[indice].value = valor;
                calcular();
                return;
            }
        }
    }

    alert("La tabla está llena");
}

document.getElementById("btnGuardarVenta")
.addEventListener("click", guardarVenta);

function guardarVenta(){

    let datos = {

        fecha: document.getElementById("fechaVenta").value,

        cliente: document.getElementById("cliente").value,

        importe_total:
            Number(document.getElementById("importeGeneral").value),

        detalles: []
    };

    agregarTipoVenta("Comercial","comercial","precioComercial","pesoTotalComercial","importeComercial",datos);
    agregarTipoVenta("Jumbo","jumbo","precioJumbo","pesoTotalJumbo","importeJumbo",datos);
    agregarTipoVenta("Pardo","pardo","precioPardo","pesoTotalPardo","importePardo",datos);

    fetch("/guardar_venta", {

        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(datos)
    })
    .then(res=>res.json())
    .then(data=>{
        alert(data.mensaje);
    });
}

function agregarTipoVenta(nombre, clase, idPrecio, idPesoTotal, idImporte, datos){

    let pesos = [];

    document.querySelectorAll("." + clase)
    .forEach(x=>{
        if(x.value!="")
            pesos.push(Number(x.value));
    });

    if(pesos.length==0) return;

    datos.detalles.push({

        tipo_huevo:nombre,

        precio_kg: Number(document.getElementById(idPrecio).value),

        peso_total: Number(document.getElementById(idPesoTotal).value),

        importe: Number(document.getElementById(idImporte).value),

        cantidad_paquetes: pesos.length,

        pesos: pesos
    });
}