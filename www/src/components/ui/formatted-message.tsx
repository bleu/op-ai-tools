import type React from "react";
import ReactMarkdown from "react-markdown";

interface FormattedMessageProps {
  content: string;
}

export const FormattedMessage: React.FC<FormattedMessageProps> = ({
  content,
}) => {
  return (
    <ReactMarkdown
      components={{
        p: ({ node, ...props }) => <p className="mb-2" {...props} />,
        ul: ({ node, ...props }) => (
          <ul className="list-disc list-inside mb-2" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="list-decimal list-inside mb-2" {...props} />
        ),
        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
        h1: ({ node, ...props }) => (
          <h1 className="text-2xl font-bold mb-2" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-xl font-bold mb-2" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="text-lg font-bold mb-2" {...props} />
        ),
        a: ({ node, ...props }) => (
          <a className="text-blue-500 hover:underline" {...props} />
        ),
        // @ts-expect-error
        code: ({ node, inline, ...props }) =>
          inline ? (
            <code className="bg-gray-100 rounded px-1" {...props} />
          ) : (
            <code className="block bg-gray-100 rounded p-2 my-2" {...props} />
          ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
};
