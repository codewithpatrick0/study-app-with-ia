import {useState, useRef} from 'react'

export function StudyMethodTitle(){
    return (
        <h1>AI Easy Study</h1>
    )
}

export function ShowImportMesh({ onMeshLoaded }){
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fileInputRef = useRef(null);
    const [meshFile, setMeshFile] = useState(null); //Fundamental tool for remember changing info

    async function handleFileChange(event){
        const newFile = event.target.files[0]; // Select the first file selected

        if (!newFile) return; // User closed the picker without choosing

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', newFile);

        try {
            const response = await fetch('http://127.0.0.1:8000/base-processing', {
                method: 'POST',
                body: formData
            })

            if (!response.ok) {
                throw new Error("El servidor respondió con un error");
            }
            setMeshFile(newFile);
            const data = await response.json();
            onMeshLoaded(data); // Send the mesh up to App

        } catch(err){
            setError('No se pudo procesar la malla. Inténtalo de nuevo.');
            console.error('error:', err)
        } finally {
            setLoading(false);
        }
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
                disabled={loading}
            >
                {loading ? 'Procesando...' : 'Insertar'}
            </button>

            {meshFile && <p className='mesh-file-name'>{meshFile.name}</p>}
            {error && <p>{error}</p>}
        </section>
    )
}

export function MeshView( {mesh} ) {
    return (
        <section className='mesh-view'>
            <h2>{mesh.career} - {mesh.university}</h2>

            <div className='cycles-grid'>
                {mesh.cycles.map((cycle) => (
                    <article key={cycle.number} className='cycle-card'>
                        <h3>Ciclo {cycle.number}</h3>
                        <ul>
                            {cycle.courses.map((course) => (
                                <li key={course}>{course}</li>
                            ))}
                        </ul>
                    </article>
                ))}
            </div>
        </section>
    )
}