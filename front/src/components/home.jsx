import {useState, useRef} from 'react'

export function StudyMethodTitle(){
    return (
        <h1>Study With IA</h1>
    )
}

export function ShowImportMesh(){
    const fileInputRef = useRef(null);
    const [meshFile, setMeshFile] = useState(null); //Fundamental tool for remember changing info

    function handleFileChange(event){
        const newFile = event.target.files[0] // Select the first file selected
        if (!newFile) return; // User closed the picker without choosing

        setMeshFile(newFile);
        console.log('Malla seleccionada:', newFile.name, newFile.type, newFile.size)
    }

    return (
        <section className="mesh-container">
            <p className='paragraph-mesh-container'>
                <strong> Inserta tu malla curricular </strong>
            </p>

            <input type="file"
                accept='.pdf'
                ref={fileInputRef}
                onChange={handleFileChange}
                hidden
            />
            
            <button
                className='import-mesh-button'
                onClick={() => fileInputRef.current.click()}
            >
                Insertar
            </button>

            {meshFile && <p>{meshFile.name}</p>}
        </section>
    )
}

