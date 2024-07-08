import type React from "react";
// import ReactMarkdown from "react-markdown";
import { Remark } from "react-remark";

interface FormattedMessageProps {
  content: string;
}

export const FormattedMessage: React.FC<FormattedMessageProps> = ({
  content,
}) => {
  return (
    <div className="prose prose-sm">
      <Remark>{content}</Remark>
    </div>
  );
};
