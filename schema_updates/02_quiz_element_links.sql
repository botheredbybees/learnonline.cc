-- Schema updates for linking quiz questions to unit elements and critical aspects

-- Junction table for questions and unit elements
CREATE TABLE quiz_question_element (
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    element_id INTEGER REFERENCES unit_element(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (question_id, element_id)
);

-- Junction table for questions and critical aspects
CREATE TABLE quiz_question_critical_aspect (
    question_id INTEGER REFERENCES quiz_question(id) NOT NULL,
    critical_aspect_id INTEGER REFERENCES unit_critical_aspect(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (question_id, critical_aspect_id)
);

-- Indexes for performance
CREATE INDEX idx_quiz_question_element_question ON quiz_question_element(question_id);
CREATE INDEX idx_quiz_question_element_element ON quiz_question_element(element_id);
CREATE INDEX idx_quiz_question_critical_aspect_question ON quiz_question_critical_aspect(question_id);
CREATE INDEX idx_quiz_question_critical_aspect_aspect ON quiz_question_critical_aspect(critical_aspect_id);