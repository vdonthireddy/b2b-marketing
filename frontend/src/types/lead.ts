import { Stage } from "./journey";

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  company: string;
  job_title?: string;
  status: string;
  value: number;
  journey_id: string;
  stage_id?: string;
  persona_id?: string;
  stage?: Stage;
  created_at: string;
  updated_at: string;
}
