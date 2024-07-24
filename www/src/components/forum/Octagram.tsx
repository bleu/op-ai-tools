interface OctagramProps {
  className?: string;
  isMobile?: boolean;
  label?: string;
}

export function Octagram({ className, isMobile, label }: OctagramProps) {
  return (
    <svg
      width={isMobile ? "20" : "16"}
      height={isMobile ? "20" : "16"}
      viewBox="0 0 17 17"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-label={label}
    >
      <g clipPath="url(#clip0_146_1752)">
        <path d="M8.5 0L10.9898 2.48979H14.5102V6.01021L17 8.5L14.5102 10.9898V14.5102H10.9898L8.5 17L6.01021 14.5102H2.48979V10.9898L0 8.5L2.48979 6.01021V2.48979H6.01021L8.5 0Z" />
      </g>
      <defs>
        <clipPath id="clip0_146_1752">
          <rect width="17" height="17" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
}
