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
  categoryColor?: string; // Add this prop to pass the color
}

export function FilterSelect({ data, categoryColor }: FilterSelectProps) {
  return (
    <Select>
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
