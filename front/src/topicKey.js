// Identifies one topic's material: StudyView stores it under this key and StudyMaterial reads it back
export function topicKey(course, unitNumber, topicIndex) {
    return `${course}::${unitNumber}::${topicIndex}`;
}
