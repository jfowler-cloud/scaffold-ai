// Shared types for Project Planner AI and Scaffold AI integration

export interface ProjectBasics {
  name: string;
  description: string;
  target_users: string;
  timeline: "1-2 days" | "1 week" | "2 weeks" | "1 month";
  budget: "<$100" | "$100-$500" | "$500-$1000" | "$1000+";
}

export interface TechnicalRequirements {
  user_count: "<100" | "100-1K" | "1K-10K" | "10K-100K" | "100K+";
  growth_rate: "Slow" | "Moderate" | "Fast";
  uptime: "Best effort" | "99%" | "99.9%" | "99.99%";
  multi_region: boolean;
  regions: string[];
  data_size: "<1GB" | "1-10GB" | "10-100GB" | "100GB-1TB" | "1TB+";
  data_sensitivity: "Public" | "Internal" | "Confidential" | "Highly Sensitive";
  backup_frequency: "Daily" | "Hourly" | "Real-time";
  response_time: "<1s" | "<500ms" | "<200ms" | "<100ms";
  heavy_computation: boolean;
  realtime_features: boolean;
  authentication: boolean;
  auth_type?: "Email/Password" | "OAuth" | "SSO" | "MFA";
  compliance: Array<"None" | "GDPR" | "HIPAA" | "SOC2" | "PCI-DSS">;
  rate_limiting: boolean;
  external_apis: boolean;
  api_list?: string;
  payment_processing: boolean;
  email_sms: boolean;
}

export interface TechnologyPreferences {
  backend_language?: "Python" | "Node.js" | "Go" | "Java" | "No preference";
  backend_framework?: "FastAPI" | "Express" | "Django" | "Spring Boot" | "No preference";
  frontend_framework?: "React" | "Vue" | "Angular" | "Svelte" | "No preference";
  mobile_app: boolean;
  database_type?: "SQL" | "NoSQL" | "Both" | "No preference";
  infrastructure?: "Serverless" | "Containers" | "VMs" | "No preference";
  cloud_provider?: "AWS" | "Azure" | "GCP" | "No preference";
}

export interface ArchitectureOption {
  name: string;
  description: string;
  stack: Record<string, string>;
  pros: string[];
  cons: string[];
  cost_estimate: string;
  monthly_cost_estimate: string;
  complexity: string;
  best_for: string;
  mermaid_diagram: string;
}

export interface CostBreakdown {
  compute: string;
  storage: string;
  database: string;
  ai_api: string;
  networking: string;
  total_monthly: string;
}

export interface ProjectPlan {
  plan_id: string;
  basics: ProjectBasics;
  technical: TechnicalRequirements;
  preferences: TechnologyPreferences;
  architecture_options: ArchitectureOption[];
  recommended_option: string;
  technology_stack: Record<string, string>;
  cost_breakdown: CostBreakdown;
  implementation_phases: string[];
  risk_assessment: string[];
  security_checklist: string[];
  next_steps: string[];
  created_at: string;
  selectedOptionIndex?: number;
}

export interface ScaffoldHandoffRequest {
  plan_id: string;
  project_plan: ProjectPlan;
  selected_architecture: ArchitectureOption;
}

export interface ScaffoldHandoffResponse {
  session_id: string;
  message: string;
  initial_graph?: any;
}

// Security types for alignment between projects
export interface SecurityIssue {
  service: string;
  issue: string;
  severity: "critical" | "high" | "medium" | "low";
  recommendation: string;
}

export interface SecurityReview {
  security_score: number; // 0-100
  passed: boolean;
  critical_issues: SecurityIssue[];
  warnings: SecurityIssue[];
  recommendations: Array<{
    service: string;
    recommendation: string;
  }>;
  compliant_services: string[];
}
