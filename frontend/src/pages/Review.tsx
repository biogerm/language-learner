import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';

const Review: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  return (
    <div style={{ padding: '24px' }}>
      <h1>Review Course: {courseId}</h1>
      <p>This is the Review mode.</p>
      <button onClick={() => navigate(`/flashcard/${courseId}`)}>
        Go to Flashcards
      </button>
      <button onClick={() => navigate(`/dictation/${courseId}`)}>
        Go to Dictation
      </button>
    </div>
  );
};

export default Review;
