-- Migration for inserting personality profiles
-- Adds 10 predefined personality profiles to the database

-- Samantha Lee
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '972e8b0a-5ccd-43d3-b6ae-5be27ded8162',
    'Samantha Lee',
    34,
    'Female',
    'San Francisco, CA',
    'Master''s Degree',
    'Married',
    1,
    'Product Manager',
    'Senior Product Manager',
    'Technology',
    145000.0,
    'Senior',
    ARRAY['analytical', 'organized', 'goal-oriented'],
    ARRAY['efficiency', 'innovation', 'work-life balance'],
    ARRAY['early adopter', 'customer-centric', 'data-driven'],
    ARRAY['UX design', 'product strategy', 'travel'],
    ARRAY['urban professional', 'fitness-focused', 'tech-savvy'],
    ARRAY['morning workouts', 'digital note-taking', 'calendar blocking'],
    ARRAY['too many meetings', 'slow decision-making', 'poor internal tools']
);

-- Miguel Santos
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    'f8c4bdd0-7d26-4a52-be10-55be63bce6fa',
    'Miguel Santos',
    29,
    'Male',
    'Austin, TX',
    'Bachelor''s Degree',
    'Single',
    0,
    'Freelance Graphic Designer',
    'Creative Consultant',
    'Design',
    72000.0,
    'Mid',
    ARRAY['creative', 'spontaneous', 'introverted'],
    ARRAY['authenticity', 'aesthetics', 'freedom'],
    ARRAY['non-conformist', 'detail-oriented', 'independent'],
    ARRAY['illustration', 'gaming', 'photography'],
    ARRAY['night owl', 'remote worker', 'coffee shop regular'],
    ARRAY['irregular sleep', 'sketchbook journaling', 'working in sprints'],
    ARRAY['client indecision', 'unreliable feedback', 'inconsistent income']
);

-- Anita Deshmukh
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '46921449-ab1a-4fc9-bf45-4fcf7c519e3c',
    'Anita Deshmukh',
    41,
    'Female',
    'London, UK',
    'PhD',
    'Divorced',
    2,
    'University Professor',
    'Associate Professor of AI',
    'Education',
    95000.0,
    'Senior',
    ARRAY['inquisitive', 'systematic', 'patient'],
    ARRAY['truth', 'education', 'impact'],
    ARRAY['evidence-based', 'cautious', 'open-minded'],
    ARRAY['machine learning', 'ethics', 'history'],
    ARRAY['academic', 'structured', 'bookworm'],
    ARRAY['early riser', 'daily reading', 'meal prepping'],
    ARRAY['bureaucracy', 'student disengagement', 'limited research funding']
);

-- Jamal Osei
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    'b65246dd-44fb-4d5d-91c1-a19406037c10',
    'Jamal Osei',
    37,
    'Male',
    'Accra, Ghana',
    'Bachelor''s Degree',
    'Married',
    3,
    'Operations Manager',
    'Regional Ops Lead',
    'Logistics',
    58000.0,
    'Mid',
    ARRAY['resilient', 'strategic', 'team-oriented'],
    ARRAY['reliability', 'discipline', 'community'],
    ARRAY['realistic', 'hands-on', 'results-driven'],
    ARRAY['supply chain trends', 'football', 'DIY projects'],
    ARRAY['commuter', 'family-first', 'early sleeper'],
    ARRAY['task lists', 'hands-on oversight', 'Friday reviews'],
    ARRAY['delivery delays', 'lack of resources', 'miscommunication']
);

-- Lisa Novak
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '0f3f6b11-25f9-486a-a663-0ebc5e7f2f02',
    'Lisa Novak',
    26,
    'Female',
    'Berlin, Germany',
    'Bachelor''s Degree',
    'In a relationship',
    0,
    'Marketing Specialist',
    'Content Strategist',
    'SaaS',
    62000.0,
    'Junior',
    ARRAY['enthusiastic', 'empathetic', 'curious'],
    ARRAY['growth', 'creativity', 'community'],
    ARRAY['optimistic', 'trend-aware', 'collaborative'],
    ARRAY['content marketing', 'sustainability', 'urban cycling'],
    ARRAY['flexible schedule', 'remote work', 'minimalist'],
    ARRAY['weekly content planning', 'Twitter scrolling', 'podcasts during commutes'],
    ARRAY['unclear goals', 'slow feedback', 'constant pivots']
);

-- Hiroshi Tanaka
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '2bb7508a-cee1-494d-b1d3-6e4bd92f5f5d',
    'Hiroshi Tanaka',
    48,
    'Male',
    'Tokyo, Japan',
    'Master''s Degree',
    'Married',
    2,
    'Finance Director',
    'CFO',
    'Manufacturing',
    180000.0,
    'Executive',
    ARRAY['pragmatic', 'cautious', 'detail-oriented'],
    ARRAY['stability', 'efficiency', 'honor'],
    ARRAY['risk-averse', 'conservative', 'deliberate'],
    ARRAY['investing', 'bonsai cultivation', 'classical music'],
    ARRAY['corporate', 'family-focused', 'quiet living'],
    ARRAY['weekly budgeting', 'early dinners', 'reviewing financial reports'],
    ARRAY['tech overpromises', 'misaligned budgets', 'unexpected audits']
);

-- Amira Khalil
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '1cf51994-d06c-4285-a1a4-d1612cdd9cf9',
    'Amira Khalil',
    31,
    'Female',
    'Dubai, UAE',
    'Master''s Degree',
    'Single',
    0,
    'UX Designer',
    'Lead UX Designer',
    'Fintech',
    98000.0,
    'Mid',
    ARRAY['empathetic', 'observant', 'problem-solver'],
    ARRAY['clarity', 'accessibility', 'empowerment'],
    ARRAY['human-centered', 'curious', 'agile'],
    ARRAY['design systems', 'photography', 'AR/VR interfaces'],
    ARRAY['co-working space regular', 'night owl', 'digital nomad-adjacent'],
    ARRAY['user testing', 'sketching on iPad', 'coffee walks'],
    ARRAY['legacy systems', 'short deadlines', 'poor handoffs']
);

-- Carlos Mendoza
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    'aa54a6db-e22c-4d64-b30f-28a5986e5b75',
    'Carlos Mendoza',
    45,
    'Male',
    'Mexico City, MX',
    'Bachelor''s Degree',
    'Married',
    2,
    'Small Business Owner',
    'Founder, Taquería Mendoza',
    'Food & Beverage',
    40000.0,
    'Owner',
    ARRAY['hardworking', 'passionate', 'pragmatic'],
    ARRAY['tradition', 'loyalty', 'independence'],
    ARRAY['hands-on', 'customer-first', 'resourceful'],
    ARRAY['local events', 'cooking', 'radio talk shows'],
    ARRAY['early riser', 'weekend worker', 'community-driven'],
    ARRAY['daily prep', 'cash flow checks', 'quick chats with regulars'],
    ARRAY['rising ingredient costs', 'staff turnover', 'permit delays']
);

-- Elena Petrova
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '66852bb2-b2fb-419a-8717-75811479499d',
    'Elena Petrova',
    23,
    'Female',
    'Sofia, Bulgaria',
    'In progress - Bachelor''s',
    'Single',
    0,
    'Intern',
    'Marketing Intern',
    'E-commerce',
    12000.0,
    'Intern',
    ARRAY['ambitious', 'eager', 'impressionable'],
    ARRAY['learning', 'visibility', 'feedback'],
    ARRAY['open-minded', 'experimental', 'attention-seeking'],
    ARRAY['social media', 'fashion trends', 'online business'],
    ARRAY['student', 'budget-conscious', 'socially active'],
    ARRAY['scrolling TikTok', 'watching tutorials', 'trying new tools'],
    ARRAY['lack of mentorship', 'unclear expectations', 'limited responsibilities']
);

-- Robert Chan
INSERT INTO personality (id, name, age, gender, location, education_level, marital_status, children, occupation, job_title, industry, income, seniority_level, personality_traits, values, attitudes, interests, lifestyle, habits, frustrations)
VALUES (
    '869602b1-7b49-45f7-8a1b-3de8b71fefa6',
    'Robert Chan',
    56,
    'Male',
    'Vancouver, Canada',
    'Master''s Degree',
    'Married',
    3,
    'Consultant',
    'Management Consultant',
    'Healthcare',
    130000.0,
    'Senior',
    ARRAY['strategic', 'experienced', 'direct'],
    ARRAY['impact', 'efficiency', 'credibility'],
    ARRAY['results-driven', 'change-resistant', 'detail-focused'],
    ARRAY['policy reform', 'skiing', 'mentoring'],
    ARRAY['travel-heavy', 'semi-retired mindset', 'luxury-inclined'],
    ARRAY['early flights', 'client check-ins', 'evening debriefs'],
    ARRAY['slow client buy-in', 'ineffective communication', 'tool fatigue']
);
