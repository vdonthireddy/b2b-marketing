export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: "admin" | "editor" | "viewer";
  team_id?: string;
  created_at: string;
}

export interface Team {
  id: string;
  name: string;
  slug: string;
  plan: string;
  created_at: string;
  member_count: number;
}
