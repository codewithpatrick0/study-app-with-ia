import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { topicKey } from '../topicKey'

const STATUS_LABELS = {
    queued: 'En cola',
    generating: 'Generando...',
    error: 'No se pudo generar',
};

// AI links open in a new tab; noopener stops the new page from controlling this one
const markdownComponents = {
    a: ({ href, children }) => (
        <a href={href} target='_blank' rel='noopener noreferrer'>{children}</a>
    ),
};

// Renders the generated study material: one card per course, one expandable panel per topic
export function StudyMaterial({ syllabi, materials }) {
    return (
        <section className='study-material'>
            {syllabi.map((syllabus) => (
                <CourseMaterial key={syllabus.course} syllabus={syllabus} materials={materials} />
            ))}
        </section>
    )
}

function CourseMaterial({ syllabus, materials }) {
    const keys = syllabus.units.flatMap((unit) =>
        unit.topics.map((_, index) => topicKey(syllabus.course, unit.number, index))
    );
    const readyCount = keys.filter((key) => materials[key]?.status === 'done').length;

    return (
        <article className='course-material'>
            <header className='course-material-header'>
                <h3>{syllabus.course}</h3>
                <p className='course-material-progress'>{readyCount} / {keys.length} temas listos</p>
            </header>
            <p className='course-material-outcome'>{syllabus.course_achievement}</p>

            {syllabus.units.map((unit) => (
                <section key={unit.number} className='unit-material'>
                    <h4>Unidad {unit.number}: {unit.title}</h4>

                    {unit.topics.map((topic, index) => (
                        <TopicCard
                            key={index}
                            topic={topic}
                            material={materials[topicKey(syllabus.course, unit.number, index)]}
                        />
                    ))}
                </section>
            ))}
        </article>
    )
}

function TopicCard({ topic, material }) {
    const status = material?.status ?? 'queued';
    const isReady = status === 'done';

    return (
        // Native <details>: expands on click and works with keyboard and screen readers for free
        <details className={`topic-card topic-${status}`}>
            {/* Until the material exists there is nothing to show, so the panel stays closed */}
            <summary onClick={(e) => { if (!isReady) e.preventDefault(); }}>
                <span className='topic-name'>{topic}</span>
                {!isReady && (
                    <span className='topic-status'>
                        {status === 'generating' && <span className='spinner spinner-small' aria-hidden='true'></span>}
                        {STATUS_LABELS[status]}
                    </span>
                )}
            </summary>

            {isReady && (
                <div className='markdown-body'>
                    {/* Raw HTML in the Markdown is not rendered, so the AI text can't inject scripts */}
                    <Markdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                        {material.markdown}
                    </Markdown>
                </div>
            )}
        </details>
    )
}
