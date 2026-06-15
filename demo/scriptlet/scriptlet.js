function download(obj, fn) {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob(
        [JSON.stringify(obj, null, 4)],
        {type:'application/json'}
    ));
    a.download = fn;
    a.click();
};

function attivi() {
    const attivi = [];
    for (const row of document.querySelectorAll('app-deposito-supersmart mat-expansion-panel')) {
        const tipologia = row.querySelector('.panel>.col-wrapper .mat-body-2').textContent;         
        const scadenza = row.querySelector('.data-importo>:nth-child(1) .mat-body-2').textContent;  
        const importo = row.querySelector('.data-importo>:nth-child(2) .mat-body-2').textContent;   
        const tasso = row.querySelector('.panel>.ng-star-inserted .mat-body-2').textContent;        
        const attivazione = row.querySelector('.labels>:nth-child(1) .normal-md').textContent;      
        const durata = row.querySelector('.labels>:nth-child(2) .normal-md').textContent;           
        const lordi = row.querySelector('.labels>:nth-child(3) .normal-md').textContent;            
        const netti = row.querySelector('.labels>:nth-child(4) .normal-md').textContent;            

        attivi.push({
            tipologia,
            scadenza,
            importo,
            tasso,
            attivazione,
            durata,
            lordi,
            netti,
        });
    }
    download(attivi, 'attivi.json')
}

function scriptlet() {
    attivi();
//    console.log('scriptlet');
//    download({foo:'bar'}, 'filename.json');
//    console.log('scriptlet');
//    download({baz:'qux'}, 'due.json');
};
