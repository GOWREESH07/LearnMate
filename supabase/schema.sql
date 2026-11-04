-- ============================================================
-- LearnMate Database Schema
-- Run this in the Supabase SQL Editor (Settings > SQL Editor)
-- ============================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE topic_state_enum AS ENUM (
  'not_started',
  'in_progress',
  'practicing',
  'mastered'
);

CREATE TYPE resource_type_enum AS ENUM (
  'video',
  'article',
  'pdf',
  'external_link'
);

CREATE TYPE quiz_generated_by_enum AS ENUM (
  'ai',
  'manual'
);

CREATE TYPE study_plan_status_enum AS ENUM (
  'draft',
  'active',
  'completed',
  'paused'
);

CREATE TYPE difficulty_enum AS ENUM (
  'beginner',
  'intermediate',
  'advanced'
);

CREATE TYPE notification_type_enum AS ENUM (
  'quiz_generated',
  'study_reminder',
  'achievement_unlocked',
  'recommendation',
  'group_invite',
  'general'
);

-- ============================================================
-- PROFILES (extends auth.users)
-- ============================================================

CREATE TABLE profiles (
  id              UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  avatar_url      TEXT,
  interests       TEXT[] DEFAULT '{}',
  study_pace      TEXT CHECK (study_pace IN ('slow', 'moderate', 'fast')) DEFAULT 'moderate',
  target_career   TEXT,
  streak_days     INTEGER DEFAULT 0,
  last_active_at  TIMESTAMPTZ DEFAULT now(),
  onboarding_done BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- COURSES (public content)
-- ============================================================

CREATE TABLE courses (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title            TEXT NOT NULL,
  description      TEXT,
  subject          TEXT NOT NULL,
  difficulty_level difficulty_enum DEFAULT 'beginner',
  thumbnail_url    TEXT,
  total_topics     INTEGER DEFAULT 0,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- TOPICS (public content)
-- ============================================================

CREATE TABLE topics (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  course_id   UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  title       TEXT NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_topics_course_id ON topics(course_id);
CREATE INDEX idx_topics_order ON topics(course_id, order_index);

-- ============================================================
-- TOPIC PROGRESS (State Pattern backing table)
-- ============================================================

CREATE TABLE topic_progress (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  topic_id    UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  state       topic_state_enum DEFAULT 'not_started',
  updated_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE (user_id, topic_id)
);

CREATE INDEX idx_topic_progress_user ON topic_progress(user_id);
CREATE INDEX idx_topic_progress_topic ON topic_progress(topic_id);

-- ============================================================
-- LEARNING RESOURCES (Factory Method + Adapter backing table)
-- ============================================================

CREATE TABLE learning_resources (
  id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  topic_id   UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  type       resource_type_enum NOT NULL,
  title      TEXT NOT NULL,
  url        TEXT NOT NULL,
  source     TEXT,
  duration   INTEGER, -- seconds for videos
  metadata   JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_resources_topic ON learning_resources(topic_id);

-- ============================================================
-- QUIZZES
-- ============================================================

CREATE TABLE quizzes (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  topic_id     UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  difficulty   difficulty_enum DEFAULT 'beginner',
  generated_by quiz_generated_by_enum DEFAULT 'manual',
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_quizzes_topic ON quizzes(topic_id);

-- ============================================================
-- QUIZ QUESTIONS
-- ============================================================

CREATE TABLE quiz_questions (
  id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quiz_id        UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  question_text  TEXT NOT NULL,
  options        JSONB NOT NULL, -- array of option strings
  correct_answer TEXT NOT NULL,
  explanation    TEXT,
  order_index    INTEGER DEFAULT 0
);

CREATE INDEX idx_questions_quiz ON quiz_questions(quiz_id);

-- ============================================================
-- QUIZ ATTEMPTS
-- ============================================================

CREATE TABLE quiz_attempts (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  quiz_id      UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
  score        FLOAT NOT NULL DEFAULT 0,
  answers      JSONB DEFAULT '{}',
  completed_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_attempts_user ON quiz_attempts(user_id);
CREATE INDEX idx_attempts_quiz ON quiz_attempts(quiz_id);
CREATE INDEX idx_attempts_completed ON quiz_attempts(user_id, completed_at DESC);

-- ============================================================
-- STUDY PLANS (Builder Pattern backing table)
-- ============================================================

CREATE TABLE study_plans (
  id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title      TEXT NOT NULL,
  goal       TEXT,
  start_date DATE NOT NULL,
  end_date   DATE NOT NULL,
  status     study_plan_status_enum DEFAULT 'draft',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_plans_user ON study_plans(user_id);

-- ============================================================
-- STUDY PLAN ITEMS
-- ============================================================

CREATE TABLE study_plan_items (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  study_plan_id    UUID NOT NULL REFERENCES study_plans(id) ON DELETE CASCADE,
  topic_id         UUID REFERENCES topics(id) ON DELETE SET NULL,
  scheduled_date   DATE NOT NULL,
  duration_minutes INTEGER DEFAULT 30,
  completed        BOOLEAN DEFAULT FALSE,
  notes            TEXT,
  created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_plan_items_plan ON study_plan_items(study_plan_id);
CREATE INDEX idx_plan_items_date ON study_plan_items(study_plan_id, scheduled_date);

-- ============================================================
-- NOTIFICATIONS (Observer Pattern backing table)
-- ============================================================

CREATE TABLE notifications (
  id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  type       notification_type_enum DEFAULT 'general',
  title      TEXT NOT NULL,
  message    TEXT NOT NULL,
  read       BOOLEAN DEFAULT FALSE,
  metadata   JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, read) WHERE read = FALSE;

-- ============================================================
-- ACHIEVEMENTS (Gamification / Decorator pattern)
-- ============================================================

CREATE TABLE achievements (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  title       TEXT NOT NULL,
  description TEXT,
  badge_icon  TEXT DEFAULT 'trophy',
  earned_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_achievements_user ON achievements(user_id);

-- ============================================================
-- CHAT MESSAGES
-- ============================================================

CREATE TABLE chat_messages (
  id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role       TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content    TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chat_user ON chat_messages(user_id);
CREATE INDEX idx_chat_created ON chat_messages(user_id, created_at DESC);

-- ============================================================
-- PERFORMANCE PREDICTIONS
-- ============================================================

CREATE TABLE performance_predictions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  topic_id        UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  predicted_score FLOAT NOT NULL CHECK (predicted_score BETWEEN 0 AND 100),
  confidence      FLOAT NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  rationale       TEXT,
  generated_at    TIMESTAMPTZ DEFAULT now(),
  UNIQUE (user_id, topic_id)
);

CREATE INDEX idx_predictions_user ON performance_predictions(user_id);

-- ============================================================
-- COLLABORATIVE GROUPS
-- ============================================================

CREATE TABLE collaborative_groups (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        TEXT NOT NULL,
  description TEXT,
  created_by  UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE group_members (
  group_id   UUID NOT NULL REFERENCES collaborative_groups(id) ON DELETE CASCADE,
  user_id    UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  joined_at  TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (group_id, user_id)
);

CREATE INDEX idx_group_members_user ON group_members(user_id);

-- ============================================================
-- UPDATED_AT TRIGGER FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at_profiles
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at_courses
  BEFORE UPDATE ON courses
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at_topics
  BEFORE UPDATE ON topics
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER set_updated_at_study_plans
  BEFORE UPDATE ON study_plans
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- AUTO-UPDATE TOPIC PROGRESS updated_at
-- ============================================================

CREATE TRIGGER set_updated_at_topic_progress
  BEFORE UPDATE ON topic_progress
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE topic_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_plan_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaborative_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE group_members ENABLE ROW LEVEL SECURITY;

-- PROFILES
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- COURSES (public read for authenticated users)
CREATE POLICY "Authenticated users can view courses" ON courses
  FOR SELECT USING (auth.role() = 'authenticated');

-- TOPICS (public read for authenticated users)
CREATE POLICY "Authenticated users can view topics" ON topics
  FOR SELECT USING (auth.role() = 'authenticated');

-- LEARNING RESOURCES (public read for authenticated users)
CREATE POLICY "Authenticated users can view resources" ON learning_resources
  FOR SELECT USING (auth.role() = 'authenticated');

-- QUIZZES (public read for authenticated users)
CREATE POLICY "Authenticated users can view quizzes" ON quizzes
  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can insert quizzes" ON quizzes
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- QUIZ QUESTIONS (public read for authenticated users)
CREATE POLICY "Authenticated users can view questions" ON quiz_questions
  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can insert questions" ON quiz_questions
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- TOPIC PROGRESS
CREATE POLICY "Users can view own progress" ON topic_progress
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own progress" ON topic_progress
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own progress" ON topic_progress
  FOR UPDATE USING (auth.uid() = user_id);

-- QUIZ ATTEMPTS
CREATE POLICY "Users can view own attempts" ON quiz_attempts
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own attempts" ON quiz_attempts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- STUDY PLANS
CREATE POLICY "Users can manage own study plans" ON study_plans
  FOR ALL USING (auth.uid() = user_id);

-- STUDY PLAN ITEMS
CREATE POLICY "Users can manage own plan items" ON study_plan_items
  FOR ALL USING (
    auth.uid() = (SELECT user_id FROM study_plans WHERE id = study_plan_id)
  );

-- NOTIFICATIONS
CREATE POLICY "Users can view own notifications" ON notifications
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own notifications" ON notifications
  FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Service can insert notifications" ON notifications
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- ACHIEVEMENTS
CREATE POLICY "Users can view own achievements" ON achievements
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Service can insert achievements" ON achievements
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- CHAT MESSAGES
CREATE POLICY "Users can manage own chat" ON chat_messages
  FOR ALL USING (auth.uid() = user_id);

-- PERFORMANCE PREDICTIONS
CREATE POLICY "Users can view own predictions" ON performance_predictions
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Service can upsert predictions" ON performance_predictions
  FOR ALL USING (auth.uid() = user_id);

-- COLLABORATIVE GROUPS
CREATE POLICY "Authenticated users can view groups" ON collaborative_groups
  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users can create groups" ON collaborative_groups
  FOR INSERT WITH CHECK (auth.uid() = created_by);

-- GROUP MEMBERS
CREATE POLICY "Authenticated users can view members" ON group_members
  FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Users can join groups" ON group_members
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can leave groups" ON group_members
  FOR DELETE USING (auth.uid() = user_id);

-- ============================================================
-- AUTO-CREATE PROFILE ON SIGNUP
-- ============================================================

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  user_name TEXT;
  user_avatar TEXT;
BEGIN
  user_name := COALESCE(
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'name',
    split_part(COALESCE(NEW.email, 'student@learnmate.app'), '@', 1),
    'Student'
  );
  
  user_avatar := COALESCE(
    NEW.raw_user_meta_data->>'avatar_url',
    NEW.raw_user_meta_data->>'picture'
  );

  INSERT INTO public.profiles (id, name, avatar_url, interests, study_pace, onboarding_done)
  VALUES (
    NEW.id,
    user_name,
    user_avatar,
    '{}',
    'moderate',
    FALSE
  )
  ON CONFLICT (id) DO UPDATE SET
    name = COALESCE(EXCLUDED.name, public.profiles.name),
    avatar_url = COALESCE(EXCLUDED.avatar_url, public.profiles.avatar_url);

  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  RAISE WARNING 'handle_new_user error: %', SQLERRM;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
