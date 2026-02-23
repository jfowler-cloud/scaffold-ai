import Flashbar from "@cloudscape-design/components/flashbar";
import { PlannerImport } from "@/lib/usePlannerImport";

interface PlannerNotificationProps {
  plannerData: PlannerImport | null;
  onDismiss: () => void;
}

export function PlannerNotification({ plannerData, onDismiss }: PlannerNotificationProps) {
  if (!plannerData) return null;

  const archPart = plannerData.architecture ? ` · ${plannerData.architecture}` : "";
  const content = `${plannerData.projectName}${archPart}. Ready to generate code and infrastructure.`;

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
