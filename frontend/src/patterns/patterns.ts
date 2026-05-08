// ==========================================
// ITERATOR PATTERN
// ==========================================
export interface Iterator<T> {
  next(): T | null;
  hasNext(): boolean;
}

export class ExerciseIterator implements Iterator<any> {
  private position = 0;
  private items: any[];

  constructor(items: any[]) {
    this.items = items;
  }

  next(): any | null {
    return this.hasNext() ? this.items[this.position++] : null;
  }

  hasNext(): boolean {
    return this.position < this.items.length;
  }
}

// ==========================================
// COMPOSITE PATTERN
// ==========================================
export abstract class CourseElement {
  abstract display(): string;
}

export class LessonElement extends CourseElement {
  private title: string;

  constructor(title: string) {
    super();
    this.title = title;
  }

  display() {
    return `  - Lesson: ${this.title}`;
  }
}

export class CourseComposite extends CourseElement {
  private title: string;
  private children: CourseElement[] = [];

  constructor(title: string) {
    super();
    this.title = title;
  }

  add(element: CourseElement) {
    this.children.push(element);
  }

  display() {
    return `Course: ${this.title}\n${this.children.map((child) => child.display()).join('\n')}`;
  }
}

// ==========================================
// PROXY PATTERN
// ==========================================
export interface ApiService {
  fetchData(url: string): Promise<any>;
}

export class RealApiService implements ApiService {
  async fetchData(url: string) {
    const response = await fetch(url);
    return response.json();
  }
}

export class ApiProxy implements ApiService {
  private cache: Map<string, any> = new Map();
  private realService: RealApiService;

  constructor(realService: RealApiService) {
    this.realService = realService;
  }

  async fetchData(url: string) {
    if (this.cache.has(url)) {
      console.log(`Proxy: Returning cached data for ${url}`);
      return this.cache.get(url);
    }
    const data = await this.realService.fetchData(url);
    this.cache.set(url, data);
    return data;
  }
}
