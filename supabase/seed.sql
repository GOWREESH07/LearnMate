-- ============================================================
-- LearnMate Seed Data
-- Run in Supabase SQL Editor (Settings > SQL Editor)
-- Populates courses, topics, learning resources, and study groups.
-- ============================================================

DO $$
DECLARE
  -- Course IDs
  course_math   UUID := uuid_generate_v4();
  course_cs     UUID := uuid_generate_v4();
  course_bio    UUID := uuid_generate_v4();
  course_phys   UUID := uuid_generate_v4();
  course_ds     UUID := uuid_generate_v4();

  -- Topic IDs (Math)
  t_algebra     UUID := uuid_generate_v4();
  t_calculus    UUID := uuid_generate_v4();
  t_stats       UUID := uuid_generate_v4();
  t_linear_alg  UUID := uuid_generate_v4();
  t_probability UUID := uuid_generate_v4();
  t_trig        UUID := uuid_generate_v4();
  t_discrete    UUID := uuid_generate_v4();
  t_num_theory  UUID := uuid_generate_v4();
  t_graph_theory UUID := uuid_generate_v4();

  -- Topic IDs (CS)
  t_algorithms  UUID := uuid_generate_v4();
  t_data_struct UUID := uuid_generate_v4();
  t_oop         UUID := uuid_generate_v4();
  t_databases   UUID := uuid_generate_v4();
  t_networks    UUID := uuid_generate_v4();
  t_os          UUID := uuid_generate_v4();
  t_security    UUID := uuid_generate_v4();
  t_compilers   UUID := uuid_generate_v4();
  t_ml_basics   UUID := uuid_generate_v4();

  -- Topic IDs (Biology)
  t_cell_bio    UUID := uuid_generate_v4();
  t_genetics    UUID := uuid_generate_v4();
  t_evolution   UUID := uuid_generate_v4();
  t_ecology     UUID := uuid_generate_v4();
  t_biochem     UUID := uuid_generate_v4();
  t_physiology  UUID := uuid_generate_v4();
  t_microbio    UUID := uuid_generate_v4();
  t_botany      UUID := uuid_generate_v4();
  t_zoology     UUID := uuid_generate_v4();

  -- Topic IDs (Physics)
  t_mechanics   UUID := uuid_generate_v4();
  t_electro     UUID := uuid_generate_v4();
  t_thermo      UUID := uuid_generate_v4();
  t_waves       UUID := uuid_generate_v4();
  t_optics      UUID := uuid_generate_v4();
  t_quantum     UUID := uuid_generate_v4();
  t_relativity  UUID := uuid_generate_v4();
  t_nuclear     UUID := uuid_generate_v4();
  t_astro       UUID := uuid_generate_v4();

  -- Topic IDs (Data Science)
  t_pandas      UUID := uuid_generate_v4();
  t_visualization UUID := uuid_generate_v4();
  t_regression  UUID := uuid_generate_v4();
  t_classification UUID := uuid_generate_v4();
  t_clustering  UUID := uuid_generate_v4();
  t_nlp         UUID := uuid_generate_v4();
  t_deep_learn  UUID := uuid_generate_v4();
  t_feature_eng UUID := uuid_generate_v4();
  t_model_eval  UUID := uuid_generate_v4();

BEGIN

-- ============================================================
-- COURSES
-- ============================================================
INSERT INTO courses (id, title, description, subject, difficulty_level, total_topics) VALUES
  (course_math,  'Advanced Mathematics',          'From algebra to graph theory — a complete mathematical journey.',                 'Mathematics',     'intermediate', 9),
  (course_cs,    'Computer Science Fundamentals', 'Algorithms, data structures, OS, networks, and more.',                           'Computer Science', 'intermediate', 9),
  (course_bio,   'Modern Biology',                'Cell biology through ecology — the science of living systems.',                   'Biology',         'beginner',     9),
  (course_phys,  'Physics Mastery',               'Classical mechanics to quantum physics and beyond.',                              'Physics',         'advanced',     9),
  (course_ds,    'Data Science in Practice',      'Hands-on data science from pandas to deep learning with real-world projects.',   'Data Science',    'intermediate', 9);

-- ============================================================
-- TOPICS — Mathematics
-- ============================================================
INSERT INTO topics (id, course_id, title, description, order_index) VALUES
  (t_algebra,    course_math, 'Algebraic Structures',     'Groups, rings, fields, and abstract algebra.',                           0),
  (t_calculus,   course_math, 'Calculus & Analysis',      'Limits, derivatives, integrals, and differential equations.',             1),
  (t_stats,      course_math, 'Statistics & Probability', 'Probability distributions and hypothesis testing.',                      2),
  (t_linear_alg, course_math, 'Linear Algebra',           'Vectors, matrices, transformations, and eigenvalues.',                   3),
  (t_probability,course_math, 'Probability Theory',       'Random variables, expectation, and limit theorems.',                      4),
  (t_trig,       course_math, 'Trigonometry & Geometry',  'Functions, identities, and coordinate geometry.',                         5),
  (t_discrete,   course_math, 'Discrete Mathematics',     'Combinatorics, logic, and set theory.',                                  6),
  (t_num_theory, course_math, 'Number Theory',            'Primes, modular arithmetic, and cryptography.',                           7),
  (t_graph_theory,course_math,'Graph Theory',             'Graphs, trees, network flows, and connectivity.',                         8);

-- ============================================================
-- TOPICS — Computer Science
-- ============================================================
INSERT INTO topics (id, course_id, title, description, order_index) VALUES
  (t_algorithms, course_cs, 'Algorithm Design & Analysis', 'Asymptotic analysis, greedy algorithms, and dynamic programming.',    0),
  (t_data_struct,course_cs, 'Data Structures',           'Arrays, trees, graphs, heaps, hash tables, and queues.',                 1),
  (t_oop,        course_cs, 'Object-Oriented Programming', 'Encapsulation, inheritance, polymorphism, and SOLID principles.',        2),
  (t_databases,  course_cs, 'Database Systems',          'Relational databases, SQL, indexing, transactions, and NoSQL.',           3),
  (t_networks,   course_cs, 'Computer Networks',         'TCP/IP stack, OSI model, HTTP/HTTPS, DNS, and sockets.',                 4),
  (t_os,         course_cs, 'Operating Systems',         'Process management, threads, virtual memory, and file systems.',         5),
  (t_security,   course_cs, 'Cybersecurity Essentials',  'Encryption, authentication, authorization, and web security.',           6),
  (t_compilers,  course_cs, 'Compiler Principles',       'Lexical analysis, parsing, AST generation, and code generation.',        7),
  (t_ml_basics,  course_cs, 'Machine Learning Basics',   'Supervised and unsupervised algorithms and evaluation.',                 8);

-- ============================================================
-- TOPICS — Biology
-- ============================================================
INSERT INTO topics (id, course_id, title, description, order_index) VALUES
  (t_cell_bio,   course_bio, 'Cell Biology',             'Cell structure, organelles, membrane transport, and energy.',            0),
  (t_genetics,   course_bio, 'Genetics & Genomics',      'DNA replication, transcription, translation, and CRISPR.',               1),
  (t_evolution,  course_bio, 'Evolutionary Biology',     'Natural selection, speciation, and phylogenetics.',                       2),
  (t_ecology,    course_bio, 'Ecology & Ecosystems',     'Biomes, food webs, nutrient cycles, and population dynamics.',           3),
  (t_biochem,    course_bio, 'Biochemistry',             'Proteins, nucleic acids, lipids, and metabolic pathways.',               4),
  (t_physiology, course_bio, 'Human Physiology',         'Organ systems, homeostasis, and nervous system.',                         5),
  (t_microbio,   course_bio, 'Microbiology',             'Bacteria, viruses, fungi, and immunology.',                              6),
  (t_botany,     course_bio, 'Plant Biology',            'Photosynthesis, plant anatomy, and vascular systems.',                    7),
  (t_zoology,    course_bio, 'Animal Behavior & Zoology','Ethology, animal diversity, and comparative anatomy.',                    8);

-- ============================================================
-- TOPICS — Physics
-- ============================================================
INSERT INTO topics (id, course_id, title, description, order_index) VALUES
  (t_mechanics,  course_phys, 'Classical Mechanics',     'Newtonian laws, work-energy, momentum, and gravity.',                    0),
  (t_electro,    course_phys, 'Electromagnetism',        'Electric fields, magnetic forces, and Maxwell equations.',               1),
  (t_thermo,     course_phys, 'Thermodynamics',          'Laws of thermodynamics, entropy, and statistical mechanics.',            2),
  (t_waves,      course_phys, 'Wave Mechanics',          'Harmonic oscillators, wave propagation, and resonance.',                 3),
  (t_optics,     course_phys, 'Optics & Light',          'Geometric optics, physical optics, reflection, and lasers.',             4),
  (t_quantum,    course_phys, 'Quantum Physics',         'Wave-particle duality, Schrödinger equation, and quantum states.',       5),
  (t_relativity, course_phys, 'Relativity Theory',       'Special and General Relativity, and spacetime geometry.',                 6),
  (t_nuclear,    course_phys, 'Nuclear & Particle Physics','Radioactive decay, nuclear fission/fusion, and Standard Model.',        7),
  (t_astro,      course_phys, 'Astrophysics & Cosmology','Stellar evolution, black holes, and the Big Bang theory.',               8);

-- ============================================================
-- TOPICS — Data Science
-- ============================================================
INSERT INTO topics (id, course_id, title, description, order_index) VALUES
  (t_pandas,     course_ds, 'Data Wrangling with Pandas','Data cleaning, filtering, aggregation, and reshaping.',                    0),
  (t_visualization,course_ds,'Data Visualization',       'Matplotlib, Seaborn, interactive plots, and storytelling.',              1),
  (t_regression, course_ds, 'Regression Analysis',       'Linear regression, multiple regression, and regularization.',            2),
  (t_classification,course_ds,'Classification Algorithms','Logistic regression, decision trees, random forests, and SVMs.',          3),
  (t_clustering, course_ds, 'Clustering & Unsupervised', 'K-means, hierarchical clustering, and PCA.',                             4),
  (t_nlp,        course_ds, 'Natural Language Processing','Text preprocessing, TF-IDF, word embeddings, and transformers.',         5),
  (t_deep_learn, course_ds, 'Deep Learning Essentials',   'Perceptrons, backpropagation, CNNs, and PyTorch.',                        6),
  (t_feature_eng,course_ds, 'Feature Engineering',       'Scaling, encoding categorical variables, and feature selection.',        7),
  (t_model_eval, course_ds, 'Model Evaluation',          'Cross-validation, hyperparameter tuning, and ROC-AUC.',                  8);

-- ============================================================
-- LEARNING RESOURCES
-- ============================================================
INSERT INTO learning_resources (id, topic_id, type, title, url, source, duration) VALUES
  (uuid_generate_v4(), t_linear_alg, 'video',   'Visualizing Matrix Multiplication & Transformations', 'https://www.youtube.com/results?search_query=linear+algebra+visual', '3Blue1Brown', 15),
  (uuid_generate_v4(), t_linear_alg, 'article', 'Eigenvalues & Eigenvectors Intuitive Guide',        'https://en.wikipedia.org/wiki/Eigenvalues_and_eigenvectors', 'Wikipedia', 10),
  (uuid_generate_v4(), t_algorithms, 'video',   'Dynamic Programming & Memoization Deep Dive',       'https://www.youtube.com/results?search_query=dynamic+programming', 'MIT OpenCourseWare', 45),
  (uuid_generate_v4(), t_cell_bio,   'article', 'Cellular Respiration & ATP Synthesis Breakdown',    'https://en.wikipedia.org/wiki/Cellular_respiration', 'Khan Academy', 20),
  (uuid_generate_v4(), t_quantum,    'video',   'The Schrödinger Equation Explained Simply',          'https://www.youtube.com/results?search_query=schrodinger+equation', 'PBS Space Time', 18),
  (uuid_generate_v4(), t_pandas,     'article', 'Pandas DataFrames Cookbook & Cheatsheet',           'https://pandas.pydata.org/docs/user_guide/10min.html', 'Pandas Official Docs', 15);

END $$;
