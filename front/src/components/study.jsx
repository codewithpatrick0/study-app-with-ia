import { useEffect, useRef, useState } from 'react'
import { UploadBorder } from './home'
import { StudyMaterial } from './material'
import { topicKey } from '../topicKey'

// Topics generated at the same time: faster than one by one, without flooding the API
const MAX_PARALLEL_TOPICS = 4;

// Asks the backend to generate the Markdown study material for one topic
async function fetchStudyMaterial(body, signal) {
    const response = await fetch('http://localhost:8000/study-material', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'include', // Send the auth cookie
        signal, // Lets us cancel pending requests when leaving the screen
    });

    if (!response.ok) {
        throw new Error(`The server responded with ${response.status}`);
    }
    const data = await response.json();
    return data.markdown;
}

// Runs async tasks with at most `limit` of them in flight
async function runWithLimit(tasks, limit) {
    let next = 0;
    async function worker() {
        while (next < tasks.length) {
            const task = tasks[next++]; // Safe: JavaScript runs this line without interruptions
            await task();
        }
    }
    await Promise.all(Array.from({ length: Math.min(limit, tasks.length) }, worker));
}

export function StudyView({ mesh, cycleNumber, onBack }) {
    const cycle = mesh.cycles.find((c) => c.number === cycleNumber);
    const [syllabi, setSyllabi] = useState([]);
    const [materials, setMaterials] = useState({}); // topicKey → { status, markdown }
    const abortRef = useRef(null);

    // Leaving the screen cancels the topics still waiting, so we don't pay for material nobody sees
    useEffect(() => () => abortRef.current?.abort(), []);

    function updateMaterial(key, value) {
        setMaterials((previous) => ({ ...previous, [key]: value })); // Function form: many updates arrive at once
    }

    async function generateMaterials(extracted) {
        abortRef.current?.abort(); // A new upload replaces the previous generation
        const controller = new AbortController();
        abortRef.current = controller;

        setSyllabi(extracted);
        setMaterials({});

        const tasks = extracted.flatMap((syllabus) =>
            syllabus.units.flatMap((unit) =>
                unit.topics.map((topic, index) => async () => {
                    if (controller.signal.aborted) return;
                    const key = topicKey(syllabus.course, unit.number, index);
                    updateMaterial(key, { status: 'generating' });
                    try {
                        const markdown = await fetchStudyMaterial({
                            career: mesh.career,
                            course: syllabus.course,
                            unit: unit.title,
                            topic,
                            course_achievement: syllabus.course_achievement,
                        }, controller.signal);
                        updateMaterial(key, { status: 'done', markdown });
                    } catch (err) {
                        if (controller.signal.aborted) return;
                        console.error('error:', err);
                        updateMaterial(key, { status: 'error' });
                    }
                })
            )
        );

        await runWithLimit(tasks, MAX_PARALLEL_TOPICS);
    }

    return (
        <main className='study-view'>
            <button type='button' className='link-button' onClick={onBack}>
                ← Volver a la malla
            </button>

            <header className='study-header'>
                <p className='study-eyebrow'>{mesh.career} · {mesh.university}</p>
                <h2 className='study-title'>Ciclo {cycleNumber}</h2>

                <ul className='course-chips'>
                    {cycle.courses.map((course) => (
                        <li key={course}>{course}</li>
                    ))}
                </ul>
            </header>

            <HaveSyllabus courses={cycle.courses} onSyllabiExtracted={generateMaterials} />

            {syllabi.length > 0 && <StudyMaterial syllabi={syllabi} materials={materials} />}
        </main>
    )
}

// Sends one syllabus to the backend and returns the extracted data (course, outcome, units).
// The cycle's courses go along so the backend can reject syllabi from other courses.
async function uploadSyllabus(file, courses) {
    const formData = new FormData();
    formData.append('file', file);
    courses.forEach((course) => formData.append('courses', course)); // Repeated field → list[str]

    const response = await fetch('http://localhost:8000/processing-syllabus', {
        method: 'POST',
        body: formData,
        credentials: 'include' // Send the auth cookie
    });

    if (!response.ok) {
        throw new Error(`${file.name}: the server responded with ${response.status}`);
    }
    return response.json();
}

export function HaveSyllabus({ courses, onSyllabiExtracted }) {
    const fileInputRef = useRef(null);
    const [syllabi, setSyllabi] = useState([]);
    const [loading, setLoading] = useState(false);

    async function handleFilesChange(event) {
        const files = Array.from(event.target.files); // FileList → real array, so .map works
        if (files.length === 0) return; // User closed the picker without choosing

        setSyllabi(files);
        setLoading(true);

        // One request per syllabus, all at the same time; allSettled keeps the ones that worked
        const results = await Promise.allSettled(files.map((file) => uploadSyllabus(file, courses)));

        const extracted = results
            .filter((result) => result.status === 'fulfilled')
            .map((result) => result.value);
        results
            .filter((result) => result.status === 'rejected')
            .forEach((result) => console.error('error:', result.reason));

        onSyllabiExtracted(extracted);
        setLoading(false);
    }

    return (
        <section className='have-syllabus'>
            <h3 className='have-syllabus-title'>Sube tus sílabos</h3>
            <p className='have-syllabus-text'>
                Sube los sílabos de tus cursos y generaremos el material de estudio de cada tema.
            </p>

            <section className='upload-box'>
                <UploadBorder />

                <p className='upload-box-label'>
                    <strong>Inserta tus sílabos</strong>
                </p>

                <input
                    type='file'
                    accept='.pdf'
                    multiple // One syllabus per course
                    ref={fileInputRef}
                    onChange={handleFilesChange}
                    hidden
                />

                <button
                    type='button'
                    className='primary-button'
                    onClick={() => fileInputRef.current.click()}
                    disabled={loading} // Avoid sending the same syllabi twice (each one is a paid AI call)
                >
                    {loading ? 'Procesando...' : 'Insertar'}
                </button>

                {syllabi.length > 0 && (
                    <ul className='upload-file-list'>
                        {syllabi.map((file) => (
                            <li key={file.name} className='upload-file-name'>{file.name}</li>
                        ))}
                    </ul>
                )}
            </section>
        </section>
    )
}
