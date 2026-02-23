"use client";

/**
 * Shows a small green shield badge on a node when security fixes have been applied.
 * Reads from data.config to determine which fixes are active.
 */
export function SecurityBadge({ config }: { config?: Record<string, unknown> }) {
  if (!config) return null;

  const fixes: string[] = [];
  if (config.encryption) fixes.push("Encrypted");
  if (config.vpc_enabled) fixes.push("VPC");
  if (config.waf_enabled) fixes.push("WAF");
  if (config.block_public_access) fixes.push("No Public Access");
  if (config.pitr) fixes.push("PITR");
  if (config.has_dlq) fixes.push("DLQ");
  if (config.tracing) fixes.push("X-Ray");
  if (config.mfa === "REQUIRED") fixes.push("MFA");
  if (config.security_headers) fixes.push("Sec Headers");

  if (fixes.length === 0) return null;

  return (
    <div
      title={`Security fixes applied: ${fixes.join(", ")}`}
      style={{
        position: "absolute",
        top: -8,
        right: -8,
        backgroundColor: "#10b981",
        borderRadius: "9999px",
        width: 18,
        height: 18,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
        cursor: "help",
        zIndex: 10,
      }}
    >
      <svg width="10" height="10" viewBox="0 0 24 24" fill="white">
        <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
      </svg>
    </div>
  );
}
