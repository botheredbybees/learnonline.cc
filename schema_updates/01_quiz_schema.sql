-- Quiz schema updates for learnonline.cc web app with enhanced question types and user feedback

-- Quiz question types enumeration
CREATE TYPE question_type AS ENUM (
    'MULTIPLE_CHOICE',
    'FILL_IN_BLANK',
    'DRAG_AND_DROP',
    'TEXT_ENTRY',
    'MATCHING'
);

-- Quiz question table with enhanced fields
CREATE TABLE quiz_question (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES unit(id) NOT NULL,
    question_text TEXT NOT NULL,
    question_type question_type NOT NULL,
    difficulty_level INTEGER DEFAULT 1,
    experience_points INTEGER DEFAULT 10,
    is_ai_generated BOOLEAN DEFAULT FALSE,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Quiz answer table with position for drag and drop
CREATE TABLE quiz_answer (
    id SERIAL PRIMARY KEY,
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    answer_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    position INTEGER, -- For drag and drop ordering
    explanation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User quiz attempt table
CREATE TABLE user_quiz_attempt (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) NOT NULL,
    unit_id INTEGER REFERENCES unit(id) NOT NULL,
    score INTEGER,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User response for text entry questions
CREATE TABLE user_text_response (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES user_quiz_attempt(id) NOT NULL,
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    response_text TEXT NOT NULL,
    is_correct BOOLEAN,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User response for drag and drop questions
CREATE TABLE user_drag_drop_response (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES user_quiz_attempt(id) NOT NULL,
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    answer_order INTEGER[] NOT NULL, -- Array of answer IDs in user's order
    is_correct BOOLEAN,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User feedback on questions
CREATE TABLE question_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES "user"(id) NOT NULL,
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    is_upvote BOOLEAN NOT NULL,
    feedback_text TEXT,
    suggested_improvement TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, question_id)
);

-- Indexes for performance
CREATE INDEX idx_quiz_question_unit_id ON quiz_question(unit_id);
CREATE INDEX idx_quiz_answer_question_id ON quiz_answer(question_id);
CREATE INDEX idx_user_quiz_attempt_user_id ON user_quiz_attempt(user_id);
CREATE INDEX idx_user_quiz_attempt_unit_id ON user_quiz_attempt(unit_id);
CREATE INDEX idx_question_feedback_question_id ON question_feedback(question_id);