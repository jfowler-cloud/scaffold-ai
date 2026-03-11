import Flashbar from "@cloudscape-design/components/flashbar";
import { PlannerImport } from "@/lib/usePlannerImport";

interface PlannerNotificationProps {
  plannerData: PlannerImport | null;
  onDismiss: () => void;
}

export function PlannerNotification({ plannerData, onDismiss }: PlannerNotificationProps) {
  if (!plannerData) return null;

  const parts: string[] = [plannerData.projectName];
  if (plannerData.architecture) {
    parts.push(plannerData.architecture);
  }
  if (plannerData.techStack && Object.keys(plannerData.techStack).length > 0) {
    parts.push(Object.values(plannerData.techStack).join(", "));
  }

  const findingsCount = plannerData.reviewFindings?.length ?? 0;
  const critHighCount = plannerData.reviewFindings?.filter(
    f => f.risk_level === "critical" || f.risk_level === "high"
  ).length ?? 0;
  const reviewPart = findingsCount > 0
    ? ` ${findingsCount} review findings${critHighCount > 0 ? ` (${critHighCount} critical/high)` : ""} included.`
    : "";

  const content = `${parts.join(" · ")}. Ready to generate architecture.${reviewPart}`;

  return (
    <div style={{ position: "fixed", top: 60, right: 20, zIndex: 1000, maxWidth: 400 }}>
      <Flashbar
        items={[
          {
            type: "success",
            dismissible: true,
            onDismiss,
            header: "Project Plan Imported",
            content,
          },
        ]}
      />
    </div>
  );
}
