export interface StageItem {
  id: string;
  text: string;
  position: number;
  content_type?: string;
}

export interface Stage {
  id: string;
  journey_id: string;
  name: string;
  description?: string;
  icon: string;
  color: string;
  position: number;
  goals: StageItem[];
  touchpoints: StageItem[];
  content: StageItem[];
}

export interface PersonaBasic {
  id: string;
  name: string;
  role_title?: string;
  avatar_color: string;
}

export interface Journey {
  id: string;
  team_id: string;
  name: string;
  description?: string;
  status: "draft" | "active" | "archived";
  created_by: string;
  creator_name?: string;
  stages: Stage[];
  stage_count?: number;
  personas: PersonaBasic[];
  persona_count?: number;
  created_at: string;
  updated_at: string;
}
