import type React from "react";
import Markdown from "react-markdown";
import rehypeRaw from "rehype-raw";

interface FormattedMessageProps {
  content: string;
}

export const FormattedMessage: React.FC<FormattedMessageProps> = ({
  content,
}) => {
  return (
    <Markdown
      rehypePlugins={[rehypeRaw]}
      components={{
        a: ({ node, ...props }) => <a {...props} className="text-blue-500" />,
      }}
    >
      {content}
    </Markdown>
  );
};
