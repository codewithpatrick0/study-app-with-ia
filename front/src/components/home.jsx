import {useState, useRef} from 'react'

export function StudyMethodTitle(){
    return (
        <h1 className='app-title'>AI Easy Study</h1>
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
            const response = await fetch('http://localhost:8000/base-processing', {
                method: 'POST',
                body: formData,
                credentials: 'include' // Send the auth cookie
            })

            if (!response.ok) {
                throw new Error("The server responded with an error while processing the mesh.");
            }
            setMeshFile(newFile);
            const data = await response.json();
            onMeshLoaded(data); // Send the mesh up to App

        } catch(err){
            setError('Error processing the mesh. Please try again.');
            console.error('error:', err)
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="mesh-container">
            {/* Dashed frame drawn in SVG so its dashes can move around the border */}
            <svg className="mesh-border" aria-hidden="true">
                <rect width="100%" height="100%" rx="20%" ry="20%" pathLength="100" />
            </svg>

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
                className='primary-button'
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

export function MeshView({ mesh }) {
    const [showCycleForm, setShowCycleForm] = useState(false);
    const [selectedCycle, setSelectedCycle] = useState(null);

    return (
        <section className='mesh-view'>
            <h2 className='mesh-title'>{mesh.career} - {mesh.university}</h2>

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

            <div className='mesh-actions'>
                <button
                    type='button'
                    className='primary-button'
                    onClick={() => setShowCycleForm(true)}
                >
                    Generar material de estudio
                </button>
            </div>

            {showCycleForm && (
                <ShowSetCycle cycleCount={mesh.cycles.length} onCycleSelected={setSelectedCycle} />
            )}

            {/* TODO: call the API to generate the markdown classes for the selected cycle */}
            {selectedCycle && <p>Ciclo seleccionado: {selectedCycle}</p>}
        </section>
    )
}

export function ShowSetCycle({ cycleCount, onCycleSelected }) {
    const [cycle, setCycle] = useState('');

    function handleSubmit(e) {
        e.preventDefault(); // Keep the page (and the loaded mesh) instead of reloading
        onCycleSelected(Number(cycle)); // Inputs give strings; send a number up
    }

    return (
        <form className='set-cycle-form' onSubmit={handleSubmit}>
            <label htmlFor='cycle-number'>¿En qué ciclo estás?</label>
            <input
                type='number'
                id='cycle-number'
                min='1'
                max={cycleCount}
                required
                value={cycle}
                onChange={(e) => setCycle(e.target.value)}
            />

            <button type='submit' className='primary-button'>Establecer ciclo</button>
        </form>
    )
}

