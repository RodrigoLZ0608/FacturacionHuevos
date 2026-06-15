    console.log("COMPRAS JS CARGADO");

    let columnasActuales = {
        comercial:1,
        jumbo:1,
        pardo:1
    };

    function generarTabla(id, clase){

        let body = document.getElementById(id);

        body.innerHTML = "";

        for(let i=0;i<20;i++){

            body.innerHTML += `
            <tr>
                <td>
                    <input
                        type="number"
                        class="peso ${clase}"
                        step="0.01">
                </td>
            </tr>
            `;
        }
        let colorClase = "total-" + clase;

        body.innerHTML += `
        <tr class="${colorClase}">
            <td>
                <input
                    type="text"
                    readonly
                    class="total-columna"
                    value="0.00">
            </td>
        </tr>
        `;
    }


    function agregarColumna(idTabla, clase){

    let tabla = document.getElementById(idTabla);
    let filas = tabla.querySelectorAll("tbody tr");

    filas.forEach(fila => {

        if(fila.classList.contains("total-" + clase)){

            let td = document.createElement("td");

            td.innerHTML = `
                <input
                    type="text"
                    readonly
                    class="total-columna"
                    value="0.00">
            `;

            fila.appendChild(td);

        }else{

            let td = document.createElement("td");

            let input = document.createElement("input");

            input.type = "number";
            input.step = "0.01";
            input.className = "peso " + clase;

            td.appendChild(input);

            fila.appendChild(td);
        }
    });

    columnasActuales[clase]++;
}

    function eliminarColumna(idTabla, clase){

        let tabla = document.getElementById(idTabla);
        let filas = tabla.querySelectorAll("tbody tr");

        filas.forEach(fila => {
            if (fila.children.length > 1) {
                fila.removeChild(fila.lastElementChild);
            }
        });

        columnasActuales[clase] = Math.max(1, columnasActuales[clase] - 1);
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

    document.getElementById("pesoTotalComercial").value =
    totalComercial.toFixed(2);

    document.getElementById("pesoTotalJumbo").value =
    totalJumbo.toFixed(2);

    document.getElementById("pesoTotalPardo").value =
    totalPardo.toFixed(2);

    let precioComercial =
    Number(document.getElementById("precioComercial").value)||0;

    let precioJumbo =
    Number(document.getElementById("precioJumbo").value)||0;

    let precioPardo =
    Number(document.getElementById("precioPardo").value)||0;

    let importeComercial =
    totalComercial * precioComercial;

    let importeJumbo =
    totalJumbo * precioJumbo;

    let importePardo =
    totalPardo * precioPardo;

    document.getElementById("importeComercial").value =
    importeComercial.toFixed(2);

    document.getElementById("importeJumbo").value =
    importeJumbo.toFixed(2);

    document.getElementById("importePardo").value =
    importePardo.toFixed(2);

    document.getElementById("importeGeneral").value =
    (importeComercial + importeJumbo + importePardo).toFixed(2);

    actualizarTotalesColumnas("comercial");
    actualizarTotalesColumnas("jumbo");
    actualizarTotalesColumnas("pardo");

    }

    document.addEventListener("input", calcular);
    function mostrarTablas(){

        document.getElementById("contenedorTablas").style.display = "flex";

        document.getElementById("seccionComercial").style.display =
        document.getElementById("chkComercial").checked
        ? "block"
        : "none";

        document.getElementById("seccionJumbo").style.display =
        document.getElementById("chkJumbo").checked
        ? "block"
        : "none";

        document.getElementById("seccionPardo").style.display =
        document.getElementById("chkPardo").checked
        ? "block"
        : "none";
    }
    function agregarPesoAutomatico(valor, tipo){

        let celdas = Array.from(document.querySelectorAll("." + tipo));

        // Detectar columnas reales (según inputs existentes)
        let columnas = [];

        celdas.forEach((celda, index) => {

            let col = index % celdas.length;

        });

        // Mejor enfoque: reconstrucción por columnas reales
        let filas = 20;
        let columnasMax = columnasActuales[tipo] || 1;

        for (let col = 0; col < columnasMax; col++) {

            for (let fila = 0; fila < filas; fila++) {

                let index = fila * columnasMax + col;

                if (celdas[index] && celdas[index].value === "") {
                    celdas[index].value = valor;
                    calcular();
                    return;
                }
            }
        }

        alert("La tabla está llena");
    }

    function obtenerMatriz(tipo){

    let tabla = document.querySelector(
        "#tabla" +
        tipo.charAt(0).toUpperCase() +
        tipo.slice(1)
    );

    let filasDOM = tabla.querySelectorAll(
        "tbody tr:not(." + "total-" + tipo + ")"
    );

    let matriz = [];

    filasDOM.forEach((tr, filaIndex)=>{

        let inputs = tr.querySelectorAll("input." + tipo);

        inputs.forEach((input, colIndex)=>{

            if(!matriz[colIndex]){
                matriz[colIndex] = [];
            }

            matriz[colIndex][filaIndex] = input;

        });

    });
    console.log(matriz);
    return matriz;
}

    document.addEventListener("keydown", function(e){

    const teclas = ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"];

    if (!teclas.includes(e.key)) return;

    let active = document.activeElement;

    if (!active.classList.contains("peso")) return;

    e.preventDefault();

    let tipo = active.classList[1];
    let matriz = obtenerMatriz(tipo);

    let filas = matriz[0].length;
    let columnas = matriz.length;

    let colActual = -1;
    let filaActual = -1;

    // buscar posición actual
    for (let c = 0; c < columnas; c++) {
        for (let f = 0; f < filas; f++) {
            if (matriz[c][f] === active) {
                colActual = c;
                filaActual = f;
                break;
            }
        }
        if (colActual !== -1) break;
    }

    let nuevaCol = colActual;
    let nuevaFila = filaActual;

    switch(e.key){

        case "ArrowUp":
            nuevaFila--;
            break;

        case "ArrowDown":
            nuevaFila++;
            break;

        case "ArrowLeft":
            nuevaCol--;
            break;

        case "ArrowRight":
            nuevaCol++;
            break;
    }

    // validar límites
    if (
        nuevaCol >= 0 &&
        nuevaCol < columnas &&
        nuevaFila >= 0 &&
        nuevaFila < filas &&
        matriz[nuevaCol][nuevaFila]
    ) {
        matriz[nuevaCol][nuevaFila].focus();
    }

});

    document.addEventListener("keydown", function(e){

        if (e.key !== "Enter") return;

        let active = document.activeElement;

        if (!active.classList.contains("peso")) return;

        e.preventDefault();

        let tipo = active.classList[1];

        let matriz = obtenerMatriz(tipo);

        let filas = matriz[0].length;
        let columnas = matriz.length;

        let colActual = -1;
        let filaActual = -1;

        // encontrar posición real
        for (let c = 0; c < columnas; c++) {
            for (let f = 0; f < filas; f++) {
                if (matriz[c][f] === active) {
                    colActual = c;
                    filaActual = f;
                    break;
                }
            }
            if (colActual !== -1) break;
        }

        /// ↓ bajar en columna
        for (let f = filaActual + 1; f < filas; f++) {
            if (matriz[colActual][f]) {
                matriz[colActual][f].focus();
                return;
            }
        }

        // → siguiente columna
        for (let c = colActual + 1; c < columnas; c++) {
            for (let f = 0; f < filas; f++) {
                if (matriz[c][f]) {
                    matriz[c][f].focus();
                    return;
                }
            }
        }

    });

    document.getElementById("btnGuardar")
    .addEventListener("click", guardarLiquidacion);

    function guardarLiquidacion(){

        let datos = {

            fecha: document.getElementById("fecha").value,

            proveedor: document.getElementById("proveedor").value,

            importe_total:
            Number(document.getElementById("importeGeneral").value),

            detalles: []
        };


        agregarTipo(
            "Comercial",
            "comercial",
            "precioComercial",
            "pesoTotalComercial",
            "importeComercial",
            datos
        );

        agregarTipo(
            "Jumbo",
            "jumbo",
            "precioJumbo",
            "pesoTotalJumbo",
            "importeJumbo",
            datos
        );

        agregarTipo(
            "Pardo",
            "pardo",
            "precioPardo",
            "pesoTotalPardo",
            "importePardo",
            datos
        );


        fetch("/guardar_liquidacion", {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body: JSON.stringify({
                ...datos,
                columnas: {
                    comercial: columnasActuales.comercial,
                    jumbo: columnasActuales.jumbo,
                    pardo: columnasActuales.pardo
                }
            })

        })
        .then(res=>res.json())
        .then(data=>{

            alert(data.mensaje);

        });

    }

    function agregarTipo(
        nombre,
        clase,
        idPrecio,
        idPesoTotal,
        idImporte,
        datos
    ){

        let pesos = [];

        document.querySelectorAll("." + clase)
    .forEach((x, index) => {

        if (x.value !== "") {

            let filas = 20;
            let posicion = index;

            pesos.push({
                valor: Number(x.value),
                posicion: posicion
            });

        }
    });


        if(pesos.length==0)
            return;


        datos.detalles.push({

            tipo_huevo:nombre,

            precio_kg:
            Number(document.getElementById(idPrecio).value),

            peso_total:
            Number(document.getElementById(idPesoTotal).value),

            importe:
            Number(document.getElementById(idImporte).value),

            cantidad_paquetes:
            pesos.length,

            pesos:pesos, 

            columnas: columnasActuales[clase]

        });

    }   

