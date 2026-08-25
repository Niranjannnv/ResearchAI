export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  is_verified: boolean;
  auth_provider: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface SourceResult {
  title: string;
  authors: string[];
  abstract?: string;
  summary?: string;
  publisher?: string;
  doi?: string;
  publication_date?: string;
  url?: string;
  source_type?: string;
  agent_type: string;
  confidence_score: number;
  citation_apa?: string;
  citation_mla?: string;
  citation_chicago?: string;
}

export interface CitationItem {
  title: string;
  apa: string;
  mla: string;
  chicago: string;
  url?: string;
  doi?: string;
}

export interface ReportContent {
  executive_summary: string;
  research_question: string;
  background_and_context?: string;
  methodology: string;
  findings: Array<{
    section: string;
    content: string;
    key_takeaways?: string[];
    evidence?: string[];
  }>;
  analysis: string;
  comparisons?: Array<{
    aspect: string;
    analysis?: string;
    positions: Array<{
      stance: string;
      sources: string[];
    }>;
  }>;
  practical_implications?: string;
  conclusions: string;
  limitations: string;
  future_directions?: string;
  references: CitationItem[];
  source_count?: number;
  domain?: string;
  query?: string;
}

export interface Report {
  id: string;
  title: string;
  query: string;
  summary?: string;
  content?: ReportContent;
  source_count?: number;
  word_count?: number;
  citation_style: string;
  is_public: boolean;
  has_pdf: boolean;
  has_docx: boolean;
  has_markdown: boolean;
  has_html: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  token_count?: number;
  metadata_?: {
    sources?: SourceResult[];
    citations?: CitationItem[];
    report_id?: string;
  };
  report_id?: string;
  created_at: string;
}

export interface Chat {
  id: string;
  title: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  message_count?: number;
  messages?: Message[];
}

export interface Bookmark {
  id: string;
  title: string;
  url?: string;
  note?: string;
  tags?: string[];
  chat_id?: string;
  report_id?: string;
  created_at: string;
}

export interface AgentStreamEvent {
  type: 'status' | 'complete' | 'error';
  node?: string;
  message?: string;
  data?: {
    source_count?: number;
    verified_count?: number;
    domain?: string;
    active_agents?: string[];
  };
  report?: ReportContent;
  report_id?: string;
  sources?: SourceResult[];
  citations?: CitationItem[];
}
