-- ============================================================
-- AVALIAÇÃO 20-70-10 — Schema do banco de dados (Supabase)
-- Execute este SQL no SQL Editor do seu projeto Supabase
-- ============================================================

CREATE TABLE empresas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome TEXT NOT NULL,
  token_gestor TEXT UNIQUE NOT NULL,
  criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE colaboradores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome TEXT NOT NULL,
  funcao TEXT,
  data_admissao DATE,
  empresa_id UUID REFERENCES empresas(id) ON DELETE CASCADE,
  ativo BOOLEAN DEFAULT TRUE,
  criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE blocos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome TEXT NOT NULL,
  ordem INTEGER NOT NULL,
  empresa_id UUID REFERENCES empresas(id) ON DELETE CASCADE
);

CREATE TABLE criterios (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  nome TEXT NOT NULL,
  descricao TEXT,
  bloco_id UUID REFERENCES blocos(id) ON DELETE CASCADE,
  empresa_id UUID REFERENCES empresas(id) ON DELETE CASCADE,
  ordem INTEGER NOT NULL,
  ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE avaliacoes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  colaborador_id UUID REFERENCES colaboradores(id) ON DELETE CASCADE,
  empresa_id UUID REFERENCES empresas(id) ON DELETE CASCADE,
  periodo TEXT NOT NULL,
  status TEXT DEFAULT 'pendente' CHECK (status IN ('pendente', 'colaborador_ok', 'gestor_ok', 'completa')),
  token_colaborador TEXT UNIQUE NOT NULL,
  token_gestor TEXT UNIQUE NOT NULL,
  criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE respostas (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  avaliacao_id UUID REFERENCES avaliacoes(id) ON DELETE CASCADE,
  criterio_id UUID REFERENCES criterios(id) ON DELETE CASCADE,
  nota_colaborador INTEGER CHECK (nota_colaborador BETWEEN 1 AND 4),
  nota_gestor INTEGER CHECK (nota_gestor BETWEEN 1 AND 4),
  preenchido_colaborador_em TIMESTAMPTZ,
  preenchido_gestor_em TIMESTAMPTZ,
  UNIQUE(avaliacao_id, criterio_id)
);
