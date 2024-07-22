import * as React from "react";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface FilterSelectProps {
  data: {
    label: string;
    options: { label: string; value: string }[];
  };
}

export function FilterSelect({ data }: FilterSelectProps) {
  return (
    <Select>
      <SelectTrigger className="w-full bg-muted focus:ring-0 focus:ring-offset-0">
        <SelectValue placeholder="All" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>{data.label}</SelectLabel>
          {data.options.map((item) => (
            <SelectItem key={item.value} value={item.value}>
              {item.label}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}
