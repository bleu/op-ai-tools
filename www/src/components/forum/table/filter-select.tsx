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
import { cn } from "@/lib/utils";
import { Octagram } from "../Octagram";
import { CATEGORY_COLORS } from "../categoryColors";

interface FilterSelectProps {
  data: {
    label: string;
    options: { label: string; value: string }[];
  };
  value: string;
  onChange: (value: string) => void;
}

export function FilterSelect({ data, value, onChange }: FilterSelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-full bg-muted focus:ring-0 focus:ring-offset-0">
        <SelectValue placeholder="All" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel className="flex items-center gap-2">
            {data.label}
          </SelectLabel>
          {data.options.map((item) => (
            <SelectItem key={item.value} value={item.value}>
              <div className="flex items-center gap-x-2">
                <Octagram
                  className={cn(
                    "size-4 fill-current",
                    //@ts-ignore
                    CATEGORY_COLORS[item.label]
                  )}
                  // @ts-ignore
                  style={{ color: `#${item.color}` }} // Pass the color to the style
                />
                {item.label}
              </div>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}
